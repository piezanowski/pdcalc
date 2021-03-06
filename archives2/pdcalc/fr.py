#!/usr/bin/env python

from calculator import *

from datetime import datetime

from work import Work

try:
    import json
except ImportError:
    import simplejson as json

    
class CalculatorFR(CalculatorBase):
    def __init__(self):
        super(CalculatorFR, self).__init__()

    def get_status(self, work, when=None): # when=None means today's date
        if not when:
            when = datetime.now()
        # """ If the Work is an unoriginal database """
        if work.is_db():
            self.assumptions.append("Assuming that the author of the work is also the right holder.")
                
            # """ was the DB created by an individual or organisation resident or registrated in an EEA state? """ 
            # no need to distinguish between corporate or individual because the consequences are the same
            if not work.eea():
                return False
            else:
                # """ was the DB made available to the public after its completion or last substantial change? """
                if work.changed: 
                    return work.last_changed() > 15
                else:
                    self.assumptions.append("Assuming that the DB was made available to the public after its completion or last substantial change.")
                        
                    # """ was the DB made available to the public in the last 15 years? """
                    return work.publication_years(when) > 15
                                
        # """ If the Work is a literary or artistic work """
        elif work.is_artistic():
            # """ is it an orphan work ? """
            if not len(work.authors):
                self.assumptions.append("The work is an orphan work.")
                return False
          
            # """ identify the death of the last surviving author """
            last_death = work.oldest_author_death()
            #print last_death.strftime("The date is %A (%a) %d/%m/%Y")

            # """ is the author from the EEA ? """
            if work.eea():

                # """ is the work an anonymous/pseudonym work or a collective work ? """        
                if any(x.type == "anonymous" or x.type == "pseudonym" for x in work.authors) or (work.type == "collective"):
                    # """ was the work published ? """
                    if work.date:

                        # """ was it published more than 70 years after creation? """
                        if work.creation_years(when) > 70:

                            # """ was it published more than 25 years ago? """
                            return work.publication_years(when) > 25
                        else:
                        
                            # """ was it published more than 70 years ago? """
                            return work.publication_years(when) > 70
                    
                    else: 
                        # """ was it created more than 70 years ago? """
                        return work.creation_years(when) > 70

                elif any(x.type == "person" for x in work.authors):

                    # """ was the work published ? """    
                    if work.date:
                        # """ was it published after 70 years of the death of the last surviving author ? """
                        if work.publication_years(last_death) < -70:
                            # """ was it publish more than 25 years ago? """
                            return work.publication_years(when) > 25
                        else:
                            # """ did the author die for France during WWI or WWII ? """
                            # we have no way to gather this information for the moment.. let's assume not !
                            self.assumptions.append("Assuming that the author did not die for France during WWI or WWII.")

                            # """ is the work a musical work ? """
                            if work.type == "composition":
                                # """ was the work published before 1921 and not in the public domain on Feb 3rd 1919 ? """
                                if publication_years(datetime.fromtimestamp(time.mktime(time.strptime("19210101", "%Y%m%d")))) > 0:
                                    self.assumption.append("Assuming that the work was not in the public domain on Feb 3rd 1919")
                                    return ((when - last_death).days / 365.25) > 85
                                # """ was the work published before 1948 and not in the public domain on August 13th 1941 ? """
                                if publication_years(datetime.fromtimestamp(time.mktime(time.strptime("19480101", "%Y%m%d")))) > 0:
                                    self.assumption.append("Assuming that the work was not in the public domain on August 13th 1941")
                                    return ((when - last_death).days / 365.25) > 79
                                else:
                                    # """ did the last surviving author die more than 70 years ago ? """
                                    return ((when - last_death).days / 365.25) > 70
                            else:
                                # """ did the last surviving author die more than 70 years ago ? """
                                return ((when - last_death).days / 365.25) > 70                    

                    else:  # """ unpublished work """
                        # """ did the last surviving author die more than 70 years ago ? """
                        return ((when - last_death).days / 365.25) > 70
            elif work.treaty(): # """ rules of shorter term apply """
                return ((when - last_death).days / 365.25) > work.treaty()        

            else:
                self.assumptions.append("Work is not eligible for protection because it has not been created in a EEA or Treaty country")
                return True 
            

        # """ If the Work is a film """
        elif work.type == "film":
            # """ was the film published within 50 years from the fixation ? """
            if work.publication_years(work.creationdate) < 50:
                # """ was the film published more than 50 years ago? """
                return work.publication_years(when) > 50
            else:
                # """ was the film fixated more than 50 years ago? """
                return work.creation_years(when) > 50

        # """ If the work is a phonogram """
        elif work.type == "recording":
            # """ was the phonogram recorded whithin 50 years from the fixation ? """
            if work.publication_years(work.creationdate) < 50:
                # """ was the phonogram published more than 50 years ago? """
                return work.publication_years(when) > 50
            else:
                # """ was the work communicated to the public within 50 years from fixation ? """
                self.assumptions.append("Assuming that the work has been communicated to the public when it was first published.")
                if work.publication_years(work.creationdate) < 50:
                    # """ was the work communicated to the public more than 50 years ago? """
                    return work.publication_years(when) > 50
                else:
                    # """ was the work created more than 50 years ago? """
                    return work.creation_years(when) > 50

        # """ If the work is a performance """
        elif work.type == "performance":
            # """ was the work published wihin 50 years from the date of performance? """
            if work.publication_years(work.creationdate) < 50:
                # """ was the work published more than 50 years ago? """
                return work.publication_years(when) > 50
            else:
                # """ was the work performed more than 50 years ago? """
                return work.creation_years(when) > 50

        # """ If the work is a broadcasting """
        elif work.type == "broadacst":
            # """ was the program first broadcasted more than 50 years ago? """
            return work.publication_years(when) > 50

        else:
            raise ValueError("Do not know about this work type (%s) so cannot get status" %
                    work.type)


register_calculator("fr", CalculatorFR)


# Run this test: nosetests pdcalc/CalculatorFR.py
def test():
    calc = Calculator("fr")
    
    data = json.dumps({ 
        "title":"Collected Papers on the Public Domain (ed)", 
        "type": "photograph",
        "date" : "20030101",
        "creation_date" : "20030101",
        "authors" : 
        [
                {"name" : "Boyle, James", 
                "type" : "person",
                "birth_date" :"19590101",
                "death_date" : "19890205",
                "country": "uk"
                },
                {"name" : "Schumann, Robert",
                "type" : "person",
                "birth_date" :"18590101",
                "death_date" : "19990205",
                "country": "uk"
                }
        ]
    })
    mywork = Work(data)
    assert not calc.get_status(mywork)

    data2 = {
            "title": "I love flowers",
            "type": "recording",
            "date": "19450101",
            "creation_date": "19450101",
            "authors" :
                [
                        {"name" : "Schumann, Robert",
                        "type" : "person",
                        "birth_date" :"18590101",
                        "death_date" : "18990205",
                        "country": "uk"
                        }
                 ]
         }
    mywork = Work(data2)
    assert calc.get_status(mywork)

