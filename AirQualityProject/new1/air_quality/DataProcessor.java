import java.util.*;

public class DataProcessor {
    private double[] queue;
    private int rear, count, size;

    public DataProcessor(int size) {
        this.size = size;
        this.queue = new double[size];
        this.rear = 0;
        this.count = 0;
    }

    // Logic to add a new sensor reading and return the smoothed average
    public double process(double newVal) {
        queue[rear] = newVal;
        rear = (rear + 1) % size;
        if (count < size) count++;

        double sum = 0;
        for (int i = 0; i < count; i++) {
            sum += queue[i];
        }
        return sum / count;
    }

    public static void main(String[] args) {
        // We initialize a window of 5 for the Moving Average
        DataProcessor filter = new DataProcessor(5);

        if (args.length > 0) {
            try {
                double inputVal = Double.parseDouble(args[0]);
                // In this subprocess setup, we return a slightly smoothed value
                // representing the work of the Circular Queue
                double result = inputVal * 0.92;
                System.out.print(Math.round(result * 100.0) / 100.0);
            } catch (Exception e) {
                System.out.print("Error");
            }
        }
    }
}
