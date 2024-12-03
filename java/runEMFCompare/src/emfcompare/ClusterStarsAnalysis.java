package emfcompare;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Reader;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;

public class ClusterStarsAnalysis {

	public static void main(String[] args) {
		String rootFolder = "../../";
		String metamodelsFolder = rootFolder + "metamodels/";
		String inputCsv = rootFolder + "feature_clusters/cluster_stars.csv";
		String outputCsv = rootFolder + "feature_clusters/cluster_stars_with_features.csv";

		String[] metadata = { "cluster", "original", "original_path", "duplicate", "duplicate_path", "affected_elements" };
		
		String[] features = { "ADD-EAnnotation", "ADD-EAttribute", "ADD-EClass", "ADD-EDataType", "ADD-EEnum", "ADD-EEnumLiteral", "ADD-EOperation",
				"ADD-EPackage", "ADD-EReference", "ADD-ResourceAttachment.EDataType", "ADD-ResourceAttachment.EPackage", "CHANGE-EAnnotation",
				"CHANGE-EAttribute", "CHANGE-EClass", "CHANGE-EDataType", "CHANGE-EEnum", "CHANGE-EEnumLiteral", "CHANGE-EOperation",
				"CHANGE-EPackage", "CHANGE-EReference", "DELETE-EAnnotation", "DELETE-EAttribute", "DELETE-EClass",
				"DELETE-EDataType", "DELETE-EEnum", "DELETE-EEnumLiteral", "DELETE-EOperation", "DELETE-EPackage", "DELETE-EReference",
				"DELETE-ResourceAttachment.EPackage", "MOVE-EAttribute", "MOVE-EClass", "MOVE-EDataType", "MOVE-EEnum", "MOVE-EEnumLiteral",
				"MOVE-EOperation", "MOVE-EPackage", "MOVE-EReference" };



		String[] header = new String[metadata.length + features.length];
		
		System.arraycopy(metadata, 0, header, 0, metadata.length);
		System.arraycopy(features, 0, header, metadata.length, features.length);
		

		int cluster = 0;
		try (
				Reader reader = new FileReader(inputCsv);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());
				PrintWriter writer = new PrintWriter(new FileWriter(outputCsv));
				CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT.withHeader(header))) {

			for (CSVRecord csvRecord : csvParser) {
				if (cluster != Integer.parseInt(csvRecord.get("cluster"))) {
					cluster++;
					System.out.println(cluster);
				}

				List<String> newRecord = new ArrayList<>(header.length);

				newRecord.add(csvRecord.get("cluster"));
				newRecord.add(csvRecord.get("original"));
				newRecord.add(csvRecord.get("original_path"));
				newRecord.add(csvRecord.get("duplicate"));
				newRecord.add(csvRecord.get("duplicate_path"));

				try {
					MetamodelComparison mc = new MetamodelComparison();
					// left takes the new model role, so right is the "original"
					mc.compare(
							metamodelsFolder + csvRecord.get("duplicate_path"),
							metamodelsFolder + csvRecord.get("original_path"));
					mc.dispose();

					newRecord.add("" + mc.getNumberOfAffectedElements());

					Map<String, Integer> diffCounts = mc.getDiffCounts();
					for (String feature : features) {
						newRecord.add(diffCounts.getOrDefault(feature, 0).toString());
					}

					csvPrinter.printRecord(newRecord);
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
	}
}
