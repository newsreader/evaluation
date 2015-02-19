package eu.fbk.newsreader.naf;

import ixa.kaflib.CLink;
import ixa.kaflib.Coref;
import ixa.kaflib.ExternalRef;
import ixa.kaflib.KAFDocument;
import ixa.kaflib.Predicate;
import ixa.kaflib.TLink;
import ixa.kaflib.Term;
import ixa.kaflib.Timex3;
import ixa.kaflib.WF;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.ListIterator;

import javax.xml.bind.JAXBException;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.xml.sax.SAXException;

public class NAFtoCAT {

	/**
	 * @param args
	 * @throws IOException 
	 * @throws SAXException 
	 * @throws ParserConfigurationException 
	 * @throws JAXBException 
	 * @throws InterruptedException 
	 * @throws TransformerException 
	 */

		
	public static void main(String[] args) throws JAXBException, ParserConfigurationException, SAXException, IOException, InterruptedException, TransformerException {
		//BufferedReader br = new BufferedReader(new FileReader(args[0]));
		
		//BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		String fileNameOut = args[1];
		
		NAF2CAT(new File(args[0]), fileNameOut);
		
		
	}
	

	public static void NAF2CAT (File f, String fileName) throws IOException, ParserConfigurationException, TransformerException{
		//KAFDocument nafFile = KAFDocument.createFromStream(br);
		KAFDocument nafFile = KAFDocument.createFromFile(f);
		ListIterator<WF> tokenList = nafFile.getWFs().listIterator();
		
		HashMap<String,String> idNAFCAT = new HashMap<String,String> ();
		
		DocumentBuilderFactory docFactory = DocumentBuilderFactory.newInstance();
		DocumentBuilder docBuilder = docFactory.newDocumentBuilder();
 
		// root elements
		Document doc = docBuilder.newDocument();
		Element rootElement = doc.createElement("Document");
		doc.appendChild(rootElement);
		 
		Attr attr = doc.createAttribute("doc_name");
		attr.setValue(fileName);
		rootElement.setAttributeNode(attr);
		
		int cptToken = 0;
		
		while(tokenList.hasNext()){
			WF w = tokenList.next();
			Element token = doc.createElement("token");
			
			Attr attrId = doc.createAttribute("t_id");
			attrId.setValue(w.getId().substring(1));
			token.setAttributeNode(attrId);
			
			Attr attrSent = doc.createAttribute("sentence");
			attrSent.setValue(Integer.toString(w.getSent()-1));
			token.setAttributeNode(attrSent);
			
			Attr attrNum = doc.createAttribute("number");
			attrNum.setValue(Integer.toString(cptToken));
			token.setAttributeNode(attrNum);
			
			token.appendChild(doc.createTextNode(w.getForm()));
			rootElement.appendChild(token);
			rootElement.appendChild(doc.createTextNode("\n"));
			
			cptToken ++;
		}
		Element markables = doc.createElement("Markables");
		
		//TIMEX3
		int tid = 1;
		
		ListIterator<Timex3> txl = nafFile.getTimeExs().listIterator();
		while (txl.hasNext()) {
			Timex3 tx3= txl.next();
			
			Element timex3 = doc.createElement("TIMEX3");
			
			idNAFCAT.put(tx3.getId(), Integer.toString(tid));
			
			timex3.setAttribute("m_id", Integer.toString(tid));
			timex3.setAttribute("functionInDocument","NONE");
			timex3.setAttribute("value", tx3.getValue());
			timex3.setAttribute("type", tx3.getType());
			
			
			if(tx3.getSpan() != null && tx3.getSpan().getTargets().size() > 0){
				ListIterator<WF> tarl = tx3.getSpan().getTargets().listIterator();
				
				while (tarl.hasNext()){
					WF t = tarl.next();
					Element tokA = doc.createElement("token_anchor");
					tokA.setAttribute("t_id", t.getId().substring(1));
					timex3.appendChild(tokA);
				}
			}
			markables.appendChild(doc.createTextNode("\n"));
			markables.appendChild(timex3);
			tid++;
		}
		
		
		//EVENT
		int mid = tid+1;
		
		List<Predicate> pl = nafFile.getPredicates();
		if(pl != null){
			ListIterator<Predicate> predl = pl.listIterator();
			while (predl.hasNext()) {
				Predicate pred = predl.next();
				
				if(pred.getSpanStr().matches(".*(\"|(\'\')|(``)|(\\[)|(\\])).*")){
				}
				else{
				//Coref co = getCoreferences(pred.getTerms().get(0).getId(),nafFile);
				
				//if(co != null){
					Element event = doc.createElement("EVENT_MENTION");
					
					event.setAttribute("m_id", Integer.toString(mid));
					
					String evType = getEventType(pred);
					if(evType != null){
						event.setAttribute("class", evType);
					}
					
					idNAFCAT.put(pred.getId(),Integer.toString(mid));
					
					ListIterator<Term> tarl = pred.getTerms().listIterator();
					
					while (tarl.hasNext()) {
						Term tar = tarl.next();
						ListIterator<WF> wfL = tar.getWFs().listIterator();
						while (wfL.hasNext()){
							Element tokA = doc.createElement("token_anchor");
							tokA.setAttribute("t_id", wfL.next().getId().substring(1));
							event.appendChild(tokA);
						}
					}
					markables.appendChild(doc.createTextNode("\n"));
					markables.appendChild(event);
					mid++;
				}
			}
		}
		
		rootElement.appendChild(doc.createTextNode("\n"));
		rootElement.appendChild(markables);
		
		Element relations = doc.createElement("Relations");
		
		//TLINK
		
		int rid = mid+1;
		
		List<TLink> tl = nafFile.getTLinks();
		if(tl != null){
			ListIterator<TLink> tlinkL = nafFile.getTLinks().listIterator();
			
			while(tlinkL.hasNext()){
				TLink tlink = tlinkL.next();
				
				if(idNAFCAT.containsKey(tlink.getFrom().getId()) && idNAFCAT.containsKey(tlink.getTo().getId())){
					Element tlinkRel = doc.createElement("TLINK");
					
					tlinkRel.setAttribute("r_id", Integer.toString(rid));
					tlinkRel.setAttribute("reltype", tlink.getRelType());
					
					Element source = doc.createElement("source");
					String mid_srce = tlink.getFrom().getId();
					if(mid_srce.equals("tmx0")){
						mid_srce = "tmx1";
					}
					source.setAttribute("m_id", idNAFCAT.get(mid_srce));
					tlinkRel.appendChild(source);
					
					Element target = doc.createElement("target");
					String mid_target = tlink.getTo().getId();
					if(mid_target.equals("tmx0")){
						mid_target = "tmx1";
					}
					target.setAttribute("m_id", idNAFCAT.get(mid_target));
					tlinkRel.appendChild(target);
					
					relations.appendChild(doc.createTextNode("\n"));
					relations.appendChild(tlinkRel);
					rid++;
				}
			}
		}
		
		//CLINK
		
		//int cid = mid+1;
				
		List<CLink> cl = nafFile.getCLinks();
		if(cl != null){
			ListIterator<CLink> clinkL = nafFile.getCLinks().listIterator();
					
			while(clinkL.hasNext()){
				CLink clink = clinkL.next();
						
				
				if(idNAFCAT.containsKey(clink.getFrom().getId()) && idNAFCAT.containsKey(clink.getTo().getId())){
					Element clinkRel = doc.createElement("CLINK");
					
					clinkRel.setAttribute("r_id", Integer.toString(rid));
					if(clink.getRelType() != null && clink.getRelType() != ""){
						clinkRel.setAttribute("reltype", clink.getRelType());
					}
							
					Element source = doc.createElement("source");
					String mid_srce = clink.getFrom().getId();
					
					source.setAttribute("m_id", idNAFCAT.get(mid_srce));
					clinkRel.appendChild(source);
							
					Element target = doc.createElement("target");
					String mid_target = clink.getTo().getId();
							
					target.setAttribute("m_id", idNAFCAT.get(mid_target));
					clinkRel.appendChild(target);
							
					relations.appendChild(doc.createTextNode("\n"));
					relations.appendChild(clinkRel);
					rid++;
				}
			}
		}
				
		
		rootElement.appendChild(doc.createTextNode("\n"));
		rootElement.appendChild(relations);
		
		TransformerFactory transformerFactory = TransformerFactory.newInstance();
		Transformer transformer = transformerFactory.newTransformer();
		DOMSource source = new DOMSource(doc);
		StreamResult result = new StreamResult(fileName);
 
		// Output to console for testing
		// StreamResult result = new StreamResult(System.out);
 
		transformer.transform(source, result);
 
		
	}
	

	/**
	 * Get a Coreferences from a term id (wid)
	 * @param wid
	 * @param nafFile
	 * @return Predicate or null
	 */
	private static Coref getCoreferences (String wid, KAFDocument nafFile) {
		ListIterator<Coref> corefl = nafFile.getCorefs().listIterator();
		while (corefl.hasNext()) {
			Coref co = corefl.next();
			if ((co.getType() != null && co.getType().equals("event")) || (co.getId().startsWith("coevent"))){
				ListIterator<Term> tarl = co.getTerms().listIterator();
				while (tarl.hasNext()) {
					Term tar = tarl.next();
					if (tar.getId().equals(wid)) {
						return co;
					}
				}
			}
		}
		return null;
	}
	
	/**
	 * Get the event type of a predicate
	 * @param pred
	 * @return
	 */
	private static String getEventType (Predicate pred){
		String eventType = "";
		ListIterator<ExternalRef> exRefl = pred.getExternalRefs().listIterator();
		while(exRefl.hasNext()){
			ExternalRef exRef = exRefl.next();
			if(exRef.getResource().equals("EventType")){
				eventType = exRef.getReference();
				//contextual, communication, cognition, grammatical
				if (eventType.equals("contextual")) eventType = "OTHER";
				else if(eventType.equals("communication") || eventType.equals("cognition")) eventType = "SPEECH_COGNITIVE";
				else if (eventType.equals("grammatical")) eventType = "GRAMMATICAL";
				else eventType = "OTHER";
			}
			else eventType = "OTHER";
		}
		return eventType;
	}

	/**
	 * Get a Predicate from a word id (wid)
	 * @param wid
	 * @param nafFile
	 * @return Predicate or null
	 */
	private static Predicate getPredicate (String wid, KAFDocument nafFile, int sent) {
		//ListIterator<Predicate> predl = nafFile.getPredicates().listIterator();
		//ListIterator<Predicate> predl = nafFile.getPredicatesBySent(sent).listIterator();
		List<Predicate> pl = nafFile.getPredicatesBySent(sent);
		if(pl != null){
			ListIterator<Predicate> predl = pl.listIterator();
			while (predl.hasNext()) {
				Predicate pred = predl.next();
				ListIterator<Term> tarl = pred.getTerms().listIterator();
				
				while (tarl.hasNext()) {
					Term tar = tarl.next();
					if (tar.getId().equals(wid)) {
						return pred;
					}
				}
			}
		}
		return null;
	}
	
	
	/**
	 * Get the DCT object
	 * @param nafFile
	 * @return Timex3 or null
	 */
	private static Timex3 getDCT (KAFDocument nafFile) {
		ListIterator<Timex3> txl = nafFile.getTimeExs().listIterator();
		while (txl.hasNext()) {
			Timex3 tx3= txl.next();
			if(tx3.getFunctionInDocument() != null && tx3.getFunctionInDocument().equals("CREATION_TIME")){
				return tx3;
			}
		}
		return null;
	}
}
