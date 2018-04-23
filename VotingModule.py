class VotingModule():
    def verify(self, ABDverdict, SBDVerdict, staticVerdict):
        alert = False
        block = False
        verdict = ""

        #Case 1
        if ABDverdict == False and SBDVerdict == False and staticVerdict == False:
            alert = False
            block = False
            verdict = "1"
        # Case 2
        elif ABDverdict == False and SBDVerdict == True and staticVerdict == False:
            alert = True
            #False
            block = True
            verdict = "2"
        # Case 3
        elif ABDverdict == True and SBDVerdict == False and staticVerdict == False:
            alert = True
            #False
            block = False
            verdict = "3"
        # Case 4
        elif ABDverdict == True and SBDVerdict == True and staticVerdict == False:
            alert = False
            block = True
            verdict = "4"
        # Case 5
        elif ABDverdict == False and SBDVerdict == False and staticVerdict == True:
            alert = True
            #False
            block = False
            verdict = "5"
        # Case 6
        elif ABDverdict == False and SBDVerdict == True and staticVerdict == True:
            alert = False
            block = True
            verdict = "6"
        # Case 7
        elif ABDverdict == True and SBDVerdict == False and staticVerdict == True:
            alert = True
            block = True
            verdict = "7"
        # Case 8
        elif ABDverdict == True and SBDVerdict == True and staticVerdict == True:
            alert = False
            block = True
            verdict = "8"

        return alert, block, verdict
