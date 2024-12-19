package emfcompare;

import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collectors;

public class TestPackageChanges {

	public static void main(String[] args) {
		String rootFolder = "packageTests/";

		String[] tests = {
				// normal root case
				"0-rootPkgChange",

				// moving a pkg from root to inside another (as a subpackage)
				// result: a root delete + a move pkg
				"10-rootPkgMovedIntoAnother",
				"11-rootPkgMovedWithEnoughChanges",

				// subpackage movement with enough changes to be an add-delete
				"2-moveSubPkg"
		};

		for (String test : tests) {
			System.out.println(test);
			String left = rootFolder + test + "/left.ecore";
			String right = rootFolder + test + "/right.ecore";

			compare(left, right);
			System.out.println("********************************************\n");
		}

	}

	public static void compare(String left, String right) {

		MetamodelComparison mc = new MetamodelComparison();
		mc.compare(left, right);

		System.out.println("Left: " + left);
		System.out.println("Right: " + right);
		System.out.println("Number of differences: " + mc.getNumberOfDifferences());
		System.out.println("Number of affected elements: " + mc.getNumberOfAffectedElements());
		System.out.println("Left size: " + mc.getLeftSize());
		System.out.println("Right size: " + mc.getRightSize());

		System.out.println("@@@@@@@@@@@@@@@@");
		Map<String, Integer> diffCounts = mc.getDiffCounts();

		System.out.println(sortMap(diffCounts));

		mc.dispose();
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
