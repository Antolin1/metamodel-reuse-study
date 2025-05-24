package emfcompare;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;

import org.eclipse.emf.compare.AttributeChange;
import org.eclipse.emf.compare.Diff;
import org.eclipse.emf.compare.DifferenceKind;
import org.eclipse.emf.compare.Match;
import org.eclipse.emf.compare.ReferenceChange;
import org.eclipse.emf.compare.ResourceAttachmentChange;
import org.eclipse.emf.ecore.EClass;

/**
 * Util functions to obtain the difference features from a meta-model comparison
 */
public class FeaturesUtil {

	public static void main(String[] args) {
		MetamodelComparison mc = new MetamodelComparison();

		String rootFolder = "../../metamodels/";

		String left = null;
		String right = null;

		try (BufferedReader br = new BufferedReader(new FileReader("compare.txt"))) {
			left = br.readLine();
			right = br.readLine();
		}
		catch (IOException e) {
			e.printStackTrace();
		}

		mc.compare(rootFolder + left, rootFolder + right);

		printFeatures("Simplified features", getSimplifiedFeatures(mc));
		printFeatures("Plain features (with the type of the feature)", getPlainFeatures(mc));

		mc = new MetamodelComparison();
		mc.setUseAllTypes(true);
		mc.compare(rootFolder + left, rootFolder + right);

		printFeatures("Features with the concrete changed elem type", getConcreteFeatures(mc));
	}

	private static void printFeatures(String header, Set<String> features) {
		System.out.println(header + ":");
		System.out.println(features.stream().collect(Collectors.joining("\n")));
		System.out.println();
	}

	/**
	 * Simplified features returned by the metamodel comparison
	 */
	public static Set<String> getSimplifiedFeatures(MetamodelComparison mc) {
		return new TreeSet<>(mc.getDiffCounts().keySet());
	}

	/**
	 * Features using the types of the EClass that
	 * contains the feature (instead of the concrete type)
	 */
	public static Set<String> getPlainFeatures(MetamodelComparison mc) {
		Set<String> features = new TreeSet<>();

		Map<Match, List<Diff>> changesMap = mc.getChangesMap();

		for (Entry<Match, List<Diff>> entry : changesMap.entrySet()) {
			for (Diff d : entry.getValue()) {
				features.add(getPlainFeature(d));
			}
		}

		for (Diff d : mc.getOtherDiffs()) {
			features.add(getPlainFeature(d));
		}

		return features;
	}

	public static String getPlainFeature(Diff d) {
		String feature = d.getKind().getLiteral();

		if (d instanceof ReferenceChange) {
			ReferenceChange rc = (ReferenceChange) d;
			feature += "-" + rc.getReference().getEContainingClass().getName() + "."
					+ rc.getReference().getName();
		}
		else if (d instanceof AttributeChange) {
			AttributeChange ac = (AttributeChange) d;
			feature += "-" + ac.getAttribute().getEContainingClass().getName() + "."
					+ ac.getAttribute().getName();
		}
		else if (d instanceof ResourceAttachmentChange) {
			ResourceAttachmentChange rac = (ResourceAttachmentChange) d;
			Match m = rac.getMatch();
			feature += "-ResourceAttachment" + ".";
			if (d.getKind() == DifferenceKind.ADD) {
				feature += m.getLeft().eClass().getName();
			}
			else if (d.getKind() == DifferenceKind.DELETE) {
				feature += m.getRight().eClass().getName();
			}
		}

		return feature;
	}

	/**
	 * Add, del and move like the simplified features, and for changes we include
	 * the feature but with the concrete type of the element being changed
	 */
	public static Set<String> getConcreteFeatures(MetamodelComparison mc) {
		Set<String> features = new TreeSet<>();

		// for add, del and moves we simply get the ones from the mc
		Map<String, Integer> diffCounts = mc.getDiffCounts();
		for (String key : diffCounts.keySet()) {
			if (key.startsWith("ADD") || key.startsWith("DELETE") || key.startsWith("MOVE")) {
				features.add(key);
			}
		}

		// for changes, use the changed type and include the feature (and treat special cases)
		Map<Match, List<Diff>> changesMap = mc.getChangesMap();

		for (Entry<Match, List<Diff>> entry : changesMap.entrySet()) {
			for (Diff d : entry.getValue()) {
				String feature = getConcreteFeature(entry.getKey(), d);
				if (feature != null) {
					features.add(feature);
				}
			}
		}

		return features;
	}

	private static String getConcreteFeature(Match m, Diff d) {
		String feature = "CHANGE-";

		if (d instanceof ReferenceChange) {
			ReferenceChange rc = (ReferenceChange) d;
			feature += getAffectedType(m).getName() + "." + rc.getReference().getName();
		}
		else if (d instanceof AttributeChange) {
			AttributeChange ac = (AttributeChange) d;
			feature += getAffectedType(m).getName() + "." + ac.getAttribute().getName();
		}
		else {
			System.out.println("Should not happen, only changes expected here");
			return null;
		}

		return feature;
	}

	private static EClass getAffectedType(Match m) {
		if (m.getLeft() != null) {
			return m.getLeft().eClass();
		}
		else {
			return m.getRight().eClass();
		}
	}

}
