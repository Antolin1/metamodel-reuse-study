package emfcompare;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Reader;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.eclipse.emf.compare.AttributeChange;
import org.eclipse.emf.compare.Diff;
import org.eclipse.emf.compare.DifferenceKind;
import org.eclipse.emf.compare.Match;
import org.eclipse.emf.compare.ReferenceChange;
import org.eclipse.emf.compare.ResourceAttachmentChange;
import org.eclipse.emf.ecore.EClass;

public class ClusterFineGrainAnalysis {

	public static void main(String[] args) {
		String rootFolder = "../../";
		String metamodelsFolder = rootFolder + "metamodels/";
		String clusterCsv = "cluster_8_changeReference.csv";
		String outputFile = clusterCsv + ".analysis.txt";

		try (
				Reader reader = new FileReader(rootFolder + clusterCsv);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());
				PrintWriter writer = new PrintWriter(new FileWriter(rootFolder + outputFile));) {

			for (CSVRecord csvRecord : csvParser) {
				Map<String, Integer> referenceDiffCounts = new HashMap<>();

				try {
					MetamodelComparison mc = new MetamodelComparison();
					// left takes the new model role, so right is the "original"
					mc.compare(
							metamodelsFolder + csvRecord.get("duplicate_path"),
							metamodelsFolder + csvRecord.get("original_path"));

					Map<Match, List<Diff>> changesMap = mc.getChangesMap();

					mc.dispose();

					writer.println(csvRecord.get("duplicate_path"));
					writer.println(csvRecord.get("original_path"));

					for (Entry<Match, List<Diff>> entry : changesMap.entrySet()) {
						if (getAffectedType(entry.getKey()).getName().equals("EReference")) {
							for (Diff d : entry.getValue()) {
								countFeatureDiff(referenceDiffCounts, d);
							}
						}
					}
					writer.println("All changes: " + sortMap(mc.getDiffCounts()));
					writer.println("Ref changes: " + sortMap(referenceDiffCounts));
					writer.println();
				}
				catch (Exception e) {
					System.out.println(csvRecord.get("duplicate_path"));
					System.out.println(csvRecord.get("original_path"));
					System.out.println(e);
				}
			}
		}
		catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("Done");
	}

	public static EClass getAffectedType(Match m) {
		if (m.getLeft() != null) {
			return m.getLeft().eClass();
		}
		else {
			return m.getRight().eClass();
		}
	}

	public static void countFeatureDiff(Map<String, Integer> diffCounts, Diff d) {
		String key = d.getKind().getLiteral();
		if (d instanceof ReferenceChange) {
			ReferenceChange rc = (ReferenceChange) d;
			key += "-" + rc.getReference().getEContainingClass().getName() + "."
					+ rc.getReference().getName();
		}
		else if (d instanceof AttributeChange) {
			AttributeChange ac = (AttributeChange) d;
			key += "-" + ac.getAttribute().getEContainingClass().getName() + "."
					+ ac.getAttribute().getName();
		}
		else if (d instanceof ResourceAttachmentChange) {
			ResourceAttachmentChange rac = (ResourceAttachmentChange) d;
			Match m = rac.getMatch();
			key += "-ResourceAttachment" + ".";
			if (d.getKind() == DifferenceKind.ADD) {
				key += m.getLeft().eClass().getName();
			}
			else if (d.getKind() == DifferenceKind.DELETE) {
				key += m.getRight().eClass().getName();
			}
		}
		diffCounts.put(key, diffCounts.getOrDefault(key, 0) + 1);
	}

	public static Map<String, Integer> sortMap(Map<String, Integer> map) {
		Map<String, Integer> sortedMap = map.entrySet()
				.stream()
				.sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))
				.collect(Collectors.toMap(
						Map.Entry::getKey,
						Map.Entry::getValue,
						(e1, e2) -> e1,
						LinkedHashMap::new // Preserve the order of sorted entries
				));
		return sortedMap;
	}
}
