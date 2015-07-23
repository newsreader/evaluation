from KafNafParserPy import *
import sys


def create_event_dict(nafobj):
    '''
    Goes through coref layer and returns dictionary of events where first occurring term is the key
    '''
    event_dict = {}
    clayer = nafobj.coreference_layer
    for coref in clayer.get_corefs():
        coref_type = coref.get_type()
        if coref_type == 'event':
            #get external references
            for myspan in coref.get_spans():
                span_ids = myspan.get_span_ids()
                firstTerm = span_ids[0]
                additionalIds = []
                for x in range(1, len(span_ids)):
                    additionalIds.append(span_ids[x])
                event_dict[firstTerm] = additionalIds
    return event_dict


def get_event_factuality_info(nafobj, eventDict):
    '''
    Takes nafobj and eventdictionary (linking event's first term to following event terms) and nafobj and creates dictionary
    where all factuality related values are associated with the term they are related to
    '''
    factDict = {}
    flayer = nafobj.factuality_layer
    for factuality in flayer.get_factualities():
        fspanIds = factuality.get_span().get_span_ids()
        fTermId = fspanIds[0]
        myvals = {}
        for fVal in factuality.get_factVals():
            myvals[fVal.get_resource()] = fVal.get_value()
        factDict[fTermId] = [myvals, 'B-Event']
        otherTerms = eventDict.get(fTermId)
        if otherTerms:
            for t in otherTerms:
                factDict[t] = [myvals, 'I-Event']
    return factDict


def create_values(myfactuals):
    '''
    turns factuality values in a correctly ordered string for conll output
    '''
    myfacts = myfactuals[0]
    event = myfactuals[1]
    pol= myfacts.get('nwr:attributionPolarity')
    cert = myfacts.get('nwr:attributionCertainty')
    time = myfacts.get('nwr:attributionTense')
    value = event + '\t' + pol + '\t' + cert + '\t' + time
    return value

def create_conll_out(nafobj):
    '''
    Takes nafobj as input and prints out a conll style file with events and their factuality marked
    '''
    myevents = create_event_dict(nafobj)
    myfactualities = get_event_factuality_info(nafobj, myevents)
    for term in nafobj.get_terms():
        termId = term.get_id()
        #take first Id of span, assuming only one token per term
        wId = term.get_span().get_span_ids()[0]
        token = nafobj.get_token(wId).get_node().text
        if termId in myfactualities:
            values = create_values(myfactualities.get(termId))
        else:
            values = 'O\tO\tO\tO'
        print token + '\t' + termId + '\t' + values






def main():

    inputfile = sys.stdin
    nafobj = KafNafParser(inputfile)
    create_conll_out(nafobj)



if __name__ == "__main__":
    main()