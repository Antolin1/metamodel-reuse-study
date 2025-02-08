package emfcompare;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Reader;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;

public class ClusterStarsAnalysisConcreteFeatures {

	public static void main(String[] args) {
		String rootFolder = "../../";
		String metamodelsFolder = rootFolder + "metamodels/";
		String inputCsv = rootFolder + "cluster_stars.csv";
		String outputCsv = rootFolder + "feature_clusters/cluster_stars_with_concrete_features.csv";

		String[] metadata = { "cluster", "original", "original_path", "duplicate", "duplicate_path", "affected_elements" };
		
		String[] features = { "ADD-EAnnotation", "ADD-EAttribute", "ADD-EClass", "ADD-EDataType", "ADD-EEnum", "ADD-EEnumLiteral", "ADD-EGenericType",
				"ADD-EObject", "ADD-EOperation", "ADD-EPackage", "ADD-EParameter", "ADD-EReference", "ADD-EStringToStringMapEntry",
				"ADD-ETypeParameter", "ADD-ResourceAttachment.EAnnotation", "ADD-ResourceAttachment.EClass", "ADD-ResourceAttachment.EDataType",
				"ADD-ResourceAttachment.EPackage", "CHANGE-EAnnotation.references", "CHANGE-EAnnotation.source", "CHANGE-EAttribute.changeable",
				"CHANGE-EAttribute.defaultValueLiteral", "CHANGE-EAttribute.derived", "CHANGE-EAttribute.eType", "CHANGE-EAttribute.iD",
				"CHANGE-EAttribute.lowerBound", "CHANGE-EAttribute.name", "CHANGE-EAttribute.ordered", "CHANGE-EAttribute.transient",
				"CHANGE-EAttribute.unique", "CHANGE-EAttribute.unsettable", "CHANGE-EAttribute.upperBound", "CHANGE-EAttribute.volatile",
				"CHANGE-EClass.abstract", "CHANGE-EClass.eSuperTypes", "CHANGE-EClass.instanceClassName", "CHANGE-EClass.instanceTypeName",
				"CHANGE-EClass.interface", "CHANGE-EClass.name", "CHANGE-EDataType.instanceClassName", "CHANGE-EDataType.instanceTypeName",
				"CHANGE-EDataType.name", "CHANGE-EDataType.serializable", "CHANGE-EEnum.instanceClassName", "CHANGE-EEnum.instanceTypeName",
				"CHANGE-EEnum.name", "CHANGE-EEnumLiteral.literal", "CHANGE-EEnumLiteral.name", "CHANGE-EEnumLiteral.value",
				"CHANGE-EGenericType.eClassifier", "CHANGE-EGenericType.eTypeParameter", "CHANGE-EOperation.eExceptions", "CHANGE-EOperation.eType",
				"CHANGE-EOperation.lowerBound", "CHANGE-EOperation.name", "CHANGE-EOperation.ordered", "CHANGE-EOperation.unique",
				"CHANGE-EOperation.upperBound", "CHANGE-EPackage.name", "CHANGE-EPackage.nsPrefix", "CHANGE-EPackage.nsURI",
				"CHANGE-EParameter.eType", "CHANGE-EParameter.lowerBound", "CHANGE-EParameter.name", "CHANGE-EParameter.ordered",
				"CHANGE-EParameter.unique", "CHANGE-EParameter.upperBound", "CHANGE-EReference.changeable", "CHANGE-EReference.containment",
				"CHANGE-EReference.defaultValueLiteral", "CHANGE-EReference.derived", "CHANGE-EReference.eKeys", "CHANGE-EReference.eOpposite",
				"CHANGE-EReference.eType", "CHANGE-EReference.lowerBound", "CHANGE-EReference.name", "CHANGE-EReference.ordered",
				"CHANGE-EReference.resolveProxies", "CHANGE-EReference.transient", "CHANGE-EReference.unique", "CHANGE-EReference.unsettable",
				"CHANGE-EReference.upperBound", "CHANGE-EReference.volatile", "CHANGE-EStringToStringMapEntry.key",
				"CHANGE-EStringToStringMapEntry.value", "DELETE-EAnnotation", "DELETE-EAttribute", "DELETE-EClass", "DELETE-EDataType",
				"DELETE-EEnum", "DELETE-EEnumLiteral", "DELETE-EGenericType", "DELETE-EOperation", "DELETE-EPackage", "DELETE-EParameter",
				"DELETE-EReference", "DELETE-EStringToStringMapEntry", "DELETE-ETypeParameter", "DELETE-ResourceAttachment.EPackage",
				"MOVE-EAttribute", "MOVE-EClass", "MOVE-EDataType", "MOVE-EEnum", "MOVE-EEnumLiteral", "MOVE-EGenericType", "MOVE-EOperation",
				"MOVE-EPackage", "MOVE-EReference" };

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
					mc.setUseAllTypes(true);
					// left takes the new model role, so right is the "original"
					mc.compare(
							metamodelsFolder + csvRecord.get("duplicate_path"),
							metamodelsFolder + csvRecord.get("original_path"));
					mc.dispose();

					newRecord.add("" + mc.getNumberOfAffectedElements());

					Set<String> foundFeatures = FeaturesUtil.getConcreteFeatures(mc);

					for (String feature : features) {
						String value = "0";
						if (foundFeatures.contains(feature)) {
							value = "1";
						}
						newRecord.add(value);
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
