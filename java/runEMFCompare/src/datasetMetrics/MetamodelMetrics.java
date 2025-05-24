package datasetMetrics;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;

/**
 * Extracts some metrics from the meta-models dataset
 */
public class MetamodelMetrics {

	public static void main(String[] args) {
		Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());

		String rootFolder = "../../";
		String metamodelsPath = rootFolder + "metamodels/";

		String outputPath = rootFolder + "metamodel_metrics.csv";

		File metamodelsFolder = new File(metamodelsPath);

		if (metamodelsFolder.exists() && metamodelsFolder.isDirectory()) {
			File[] files = metamodelsFolder.listFiles();

			if (files != null) {
				String[] headers =
						{ "name", "size_kb", "numelements", "EClasses", "EAttributes", "EReferences", "EPackages", "EAnnotations", "RootPackages" };

				try (FileWriter writer = new FileWriter(outputPath);
						CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT.withHeader(headers))) {

					int count = 0;
					for (File file : files) {

						count++;
						System.out.println(count);
						System.out.println(file.getName());

						// to avoid OS config files (e.g. mac ds-store ones)
						if (!file.getName().endsWith(".ecore")) {
							continue;
						}

						URI uri = URI.createFileURI(file.getAbsolutePath());

						ResourceSet rs = new ResourceSetImpl();
						Resource r = rs.getResource(uri, true);

						// metrics here
						List<String> record = new ArrayList<>();
						record.add(file.getName());

						// File size
						long fileSizeInBytes = file.length();
						double fileSizeInKB = (double) fileSizeInBytes / 1024;
						fileSizeInKB = Math.round(fileSizeInKB * 100.0) / 100.0;


						Map<String, Integer> counts = countElements(r);

						csvPrinter.printRecord(
								file.getName(),
								fileSizeInKB,
								countAllElements(counts),
								counts.getOrDefault("EClass", 0),
								counts.getOrDefault("EAttribute", 0),
								counts.getOrDefault("EReference", 0),
								counts.getOrDefault("EPackage", 0),
								counts.getOrDefault("EAnnotation", 0),
								countRootPackages(r));

						// dispose the model
						r.unload();


					}
				}
				catch (IOException e) {
					System.err.println("An error occurred while creating the CSV file: " + e.getMessage());
				}
			}
			else {
				System.out.println("The folder is empty or cannot be accessed.");
			}
		}
		else {
			System.out.println("The specified path is not a valid directory.");
		}
	}

	public static int countAllElements(Map<String, Integer> counts) {
		int count = 0;
		for (Entry<String, Integer> entry : counts.entrySet()) {
			count += entry.getValue();
		}
		return count;
	}

	public static Map<String, Integer> countElements(Resource resource) {
		Map<String, Integer> counts = new HashMap<>();

		// Use EcoreUtil to get all contents in the resource
		Iterator<EObject> allContents = EcoreUtil.getAllContents(resource.getContents(), false);

		while (allContents.hasNext()) {
			EObject elem = allContents.next();

			String key = elem.eClass().getName();
			counts.put(key, counts.getOrDefault(key, 0) + 1);
		}

		return counts;
	}

	public static int countRootPackages(Resource resource) {
		int rootPackages = 0;

		for (EObject eobj : resource.getContents()) {
			if (eobj instanceof EPackage) {
				rootPackages++;
			}
		}

		return rootPackages;
	}
}
