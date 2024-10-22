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
		String inputCsv = "cluster_stars.csv";
		String outputCsv = "cluster_stars_with_features.csv";

		String[] metadata = { "cluster", "original", "original_path", "duplicate", "duplicate_path", "affected_elements" };
		
		String[] features = { "ADD-EAnnotation.contents", "ADD-EAnnotation.details", "ADD-EAnnotation.references", "ADD-EClass.eGenericSuperTypes",
				"ADD-EClass.eOperations", "ADD-EClass.eStructuralFeatures", "ADD-EClass.eSuperTypes", "ADD-EClassifier.eTypeParameters",
				"ADD-EEnum.eLiterals", "ADD-EGenericType.eTypeArguments", "ADD-EModelElement.eAnnotations", "ADD-EOperation.eExceptions",
				"ADD-EOperation.eParameters", "ADD-EOperation.eTypeParameters", "ADD-EPackage.eClassifiers", "ADD-EPackage.eSubpackages",
				"ADD-EReference.eKeys", "ADD-ETypeParameter.eBounds", "ADD-ETypedElement.eGenericType", "ADD-ResourceAttachment.EAnnotation",
				"ADD-ResourceAttachment.EDataType", "ADD-ResourceAttachment.EPackage", "CHANGE-EAnnotation.source", "CHANGE-EAttribute.iD",
				"CHANGE-EClass.abstract", "CHANGE-EClass.interface", "CHANGE-EClassifier.instanceClassName", "CHANGE-EClassifier.instanceTypeName",
				"CHANGE-EDataType.serializable", "CHANGE-EEnumLiteral.literal", "CHANGE-EEnumLiteral.value", "CHANGE-ENamedElement.name",
				"CHANGE-EPackage.nsPrefix", "CHANGE-EPackage.nsURI", "CHANGE-EReference.containment", "CHANGE-EReference.resolveProxies",
				"CHANGE-EStringToStringMapEntry.key", "CHANGE-EStringToStringMapEntry.value", "CHANGE-EStructuralFeature.changeable",
				"CHANGE-EStructuralFeature.defaultValueLiteral", "CHANGE-EStructuralFeature.derived", "CHANGE-EStructuralFeature.transient",
				"CHANGE-EStructuralFeature.unsettable", "CHANGE-EStructuralFeature.volatile", "CHANGE-ETypedElement.eType",
				"CHANGE-ETypedElement.lowerBound", "CHANGE-ETypedElement.ordered", "CHANGE-ETypedElement.unique", "CHANGE-ETypedElement.upperBound",
				"DELETE-EAnnotation.contents", "DELETE-EAnnotation.details", "DELETE-EAnnotation.references", "DELETE-EClass.eGenericSuperTypes",
				"DELETE-EClass.eOperations", "DELETE-EClass.eStructuralFeatures", "DELETE-EClass.eSuperTypes", "DELETE-EClassifier.eTypeParameters",
				"DELETE-EEnum.eLiterals", "DELETE-EGenericType.eLowerBound", "DELETE-EGenericType.eTypeArguments", "DELETE-EGenericType.eUpperBound",
				"DELETE-EModelElement.eAnnotations", "DELETE-EOperation.eExceptions", "DELETE-EOperation.eParameters",
				"DELETE-EOperation.eTypeParameters", "DELETE-EPackage.eClassifiers", "DELETE-EPackage.eSubpackages", "DELETE-EReference.eKeys",
				"DELETE-ETypeParameter.eBounds", "DELETE-ETypedElement.eGenericType", "DELETE-ResourceAttachment.EPackage",
				"MOVE-EAnnotation.contents", "MOVE-EClass.eGenericSuperTypes", "MOVE-EClass.eOperations", "MOVE-EClass.eStructuralFeatures",
				"MOVE-EEnum.eLiterals", "MOVE-EGenericType.eTypeArguments", "MOVE-EGenericType.eUpperBound", "MOVE-EPackage.eClassifiers",
				"MOVE-EPackage.eSubpackages", "MOVE-ETypeParameter.eBounds", "MOVE-ETypedElement.eGenericType" };


		String[] header = new String[metadata.length + features.length];
		
		System.arraycopy(metadata, 0, header, 0, metadata.length);
		System.arraycopy(features, 0, header, metadata.length, features.length);
		

		int cluster = 0;
		try (
				Reader reader = new FileReader(rootFolder + inputCsv);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());
				PrintWriter writer = new PrintWriter(new FileWriter(rootFolder + outputCsv));
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
