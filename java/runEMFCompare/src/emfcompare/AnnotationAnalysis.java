package emfcompare;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map.Entry;
import java.util.Set;
import java.util.regex.Pattern;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.eclipse.emf.compare.Diff;
import org.eclipse.emf.compare.Match;
import org.eclipse.emf.compare.ReferenceChange;
import org.eclipse.emf.ecore.EAnnotation;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EcorePackage;

public class AnnotationAnalysis {

	public static Pattern NEW_LINE_PATTERN = Pattern.compile("\\r?\\n");

	public static void main(String[] args) {
		String rootFolder = "../../";
		String metamodelsFolder = rootFolder + "metamodels/";
		String inputFile = rootFolder + "metamodel_changes_analysis/samples/comparisons_with_annotation_changes.csv";
		String outputFile = inputFile + ".analysis.txt";

		try (
				Reader reader = new FileReader(inputFile);
				CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());
				PrintWriter writer = new PrintWriter(new FileWriter(outputFile));) {

			int counter = 0;
			List<Set<String>> annotationSourcesByComparison = new ArrayList<>();
			for (CSVRecord csvRecord : csvParser) {
				try {
					MetamodelComparison mc = new MetamodelComparison();
					mc.setUseAllTypes(true);
					// left takes the new model role, so right is the "original"
					mc.compare(
							metamodelsFolder + csvRecord.get("duplicate_path"),
							metamodelsFolder + csvRecord.get("original_path"));

					Set<String> annotationSources = new HashSet<>();
					annotationSourcesByComparison.add(annotationSources);

					for (Entry<Match, List<Diff>> entry : mc.getChangesMap().entrySet()) {
						Match m = entry.getKey();
						if (isAnnotationRelated(m)) {
							EAnnotation left = getAnnotation(m.getLeft());
							EAnnotation right = getAnnotation(m.getRight());

							if (left.getSource() != null && left.getSource().equals(right.getSource())) {
								annotationSources.add(processSource(left.getSource()));
							}
							else {
								// if the source changes, we add both versions
								if (left.getSource() != null) {
									annotationSources.add(processSource(left.getSource()));
								}
								if (right.getSource() != null) {
									annotationSources.add(processSource(right.getSource()));
								}
							}
						}
					}

					for (Diff d : mc.getOtherDiffs()) {
						if (isAnnotationRelated(d)) {
							EAnnotation a = (EAnnotation) ((ReferenceChange) d).getValue();

							if (a != null && a.getSource() != null) {
								annotationSources.add(processSource(a.getSource()));
							}
						}
					}

					System.out.println(counter);
					counter++;

					writer.println(String.join(",", annotationSources));
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

	public static String processSource(String source) {
		String cleaned = NEW_LINE_PATTERN.matcher(source).replaceAll("");
		return "\"" + cleaned + "\"";
	}

	public static EAnnotation getAnnotation(EObject obj) {
		if (obj != null) {
			if (obj.eClass().equals(EcorePackage.Literals.EANNOTATION)) {
				return (EAnnotation) obj;
			}
			else if (obj.eClass().equals(EcorePackage.Literals.ESTRING_TO_STRING_MAP_ENTRY) &&
					obj.eContainer() != null &&
					obj.eContainer().eClass().equals(EcorePackage.Literals.EANNOTATION)) {

					return (EAnnotation) obj.eContainer();
			}
		}
		return null;
	}

	public static boolean isAnnotationRelated(Match m) {
		EClass matchType = getAffectedType(m);

		// if the matched element is an annotation or a map entry
		return matchType.equals(EcorePackage.Literals.EANNOTATION) ||
				matchType.equals(EcorePackage.Literals.ESTRING_TO_STRING_MAP_ENTRY);
	}

	public static boolean isAnnotationRelated(Diff d) {
		if (d instanceof ReferenceChange) {
			ReferenceChange rc = (ReferenceChange) d;
			if (rc.getReference().getName().equals("eAnnotations")) {
				return true;
			}
		}
		return false;
	}

	public static EClass getAffectedType(Match m) {
		if (m.getLeft() != null) {
			return m.getLeft().eClass();
		}
		else {
			return m.getRight().eClass();
		}
	}

	public static EClass getAffectedType(Diff d) {
		return getAffectedType(d.getMatch());
	}

}
