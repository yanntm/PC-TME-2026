package pc;

import java.io.PrintWriter;
import java.io.FileNotFoundException;

public class RepeatBenchmark {

	public static void main(String[] args) throws FileNotFoundException {
		int[] ns = { 100, 1000, 10000, 50000, 100_000, 200_000, 300_000/* , 500000, 1000000 */ };

		PrintWriter writer = new PrintWriter("benchmark.csv");
		writer.println("N,Strategy,Time(us)");

		benchmark(Strategy.NAIVE, ns, writer);
		benchmark(Strategy.BUILDER_DEFAULT, ns, writer);
		benchmark(Strategy.BUILDER_CAPACITY, ns, writer);

		writer.close();
	}

	private static void benchmark(Strategy strategy, int[] ns, PrintWriter writer) {
		for (int n : ns) {
			long start = System.nanoTime();
			switch (strategy) {
			case NAIVE:
				Repeat.repeatNaive('a', n);
				break;
			case BUILDER_DEFAULT:
				Repeat.repeatDefault('a', n);
				break;
			case BUILDER_CAPACITY:
				Repeat.repeatCapacity('a', n);
				break;
			}
			long total = (System.nanoTime() - start);
			long elapsed = total / 1_000; // nano to micro
			writer.println(n + "," + strategy.name().toLowerCase() + "," + elapsed);
		}
	}

	public enum Strategy {
		NAIVE, BUILDER_DEFAULT, BUILDER_CAPACITY
	}

}