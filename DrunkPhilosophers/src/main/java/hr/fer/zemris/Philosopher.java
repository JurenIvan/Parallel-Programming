package hr.fer.zemris;

import mpi.MPI;
import mpi.Status;

import java.util.List;

import static hr.fer.zemris.Philosopher.ForkState.*;
import static java.lang.Math.random;
import static java.lang.Math.round;
import static java.lang.Thread.sleep;

public class Philosopher {

    private static final int GRANT_FORK = 69;
    private static final int BEG_FOR_FORK = 420;
    private static final int CHECK_FOR_REQUEST_INTERVAL = 500;
    private static final boolean[] EMPTY = new boolean[0];

    private static int rank, size;
    private static ForkState leftFork, rightFork;
    private static boolean leftRequesed, rightRequested;

    public static void main(String[] args) throws InterruptedException {
        MPI.Init(args);
        initEnvironment();

        think();
        while (missingAnyFork()) {
            if (leftFork == NON_EXISTANT) {
                MPI.COMM_WORLD.Isend(new boolean[0], 0, 0, MPI.NULL, leftNeighbour(), BEG_FOR_FORK);
                leftFork = ASKED_BUT_NO_ANSWER;
            }
            var message = MPI.COMM_WORLD.Recv(new boolean[0], 0, 0, MPI.NULL, MPI.ANY_SOURCE, MPI.ANY_TAG);
            var receivedGrant = responseToMessage(message);
            if (!receivedGrant) continue;

            if (rightFork == NON_EXISTANT) {
                MPI.COMM_WORLD.Isend(new boolean[0], 0, 0, MPI.NULL, rightNeighbour(), BEG_FOR_FORK);
                rightFork = ASKED_BUT_NO_ANSWER;
            }
            message = MPI.COMM_WORLD.Recv(new boolean[0], 0, 0, MPI.NULL, MPI.ANY_SOURCE, MPI.ANY_TAG);
            responseToMessage(message);
        }
        eat();
        respondIfNeeded();

        MPI.Finalize();
    }

    private static void respondIfNeeded() {
        if (leftRequesed) {
            leftFork = NON_EXISTANT;
            MPI.COMM_WORLD.Isend(EMPTY, 0, 0, MPI.NULL, leftNeighbour(), GRANT_FORK);
        }
        if (rightRequested) {
            rightFork = NON_EXISTANT;
            MPI.COMM_WORLD.Isend(EMPTY, 0, 0, MPI.NULL, rightNeighbour(), GRANT_FORK);
        }
    }

    private static boolean missingAnyFork() {
        return leftFork == NON_EXISTANT || leftFork == ASKED_BUT_NO_ANSWER || rightFork == NON_EXISTANT || rightFork == ASKED_BUT_NO_ANSWER;
    }

    private static boolean missingLeftFork() {
        return leftFork == NON_EXISTANT || leftFork == ASKED_BUT_NO_ANSWER;
    }

    private static boolean missingRight() {
        return leftFork == NON_EXISTANT || leftFork == ASKED_BUT_NO_ANSWER;
    }

    private static boolean responseToMessage(Status message) {
        if (message.tag == GRANT_FORK) {
            if (message.source == leftNeighbour()) leftFork = CLEAN;
            else rightFork = CLEAN;
            return false;
        }
        if (message.tag == BEG_FOR_FORK) {
            if (message.source == leftNeighbour()) {
                if (leftFork == CLEAN) {
                    leftRequesed = true;
                } else {
                    leftFork = NON_EXISTANT;
                    MPI.COMM_WORLD.Isend(EMPTY, 0, 0, MPI.NULL, leftNeighbour(), GRANT_FORK);
                }
            } else {
                if (rightFork == CLEAN) {
                    rightRequested = true;
                } else {
                    rightFork = NON_EXISTANT;
                    MPI.COMM_WORLD.Isend(EMPTY, 0, 0, MPI.NULL, rightNeighbour(), GRANT_FORK);
                }
            }
        }
        return true;
    }

    private static void eat() {
        System.out.println(rank + " EATING");
        rightFork = leftFork = DIRTY;
    }

    private static void think() throws InterruptedException {
        System.out.println(rank + " THINKING");
        var sleepLen = randomNumberInRange(1000, 10000);
        for (int i = 0; i < sleepLen; i += CHECK_FOR_REQUEST_INTERVAL) {
            sleep(CHECK_FOR_REQUEST_INTERVAL);

            for (var neighbour : List.of(leftNeighbour(), rightNeighbour())) {
                if (MPI.COMM_WORLD.Iprobe(neighbour, BEG_FOR_FORK).count > 0)
                    responseToMessage(MPI.COMM_WORLD.Probe(neighbour, BEG_FOR_FORK));
            }
        }
    }

    private static void initEnvironment() {
        rank = MPI.COMM_WORLD.Rank();
        size = MPI.COMM_WORLD.Size();
        rightFork = rank == 0 ? DIRTY : NON_EXISTANT;
        leftFork = rank + 1 == size ? NON_EXISTANT : DIRTY;
    }

    private static long randomNumberInRange(int min, int max) {
        return round(random() * (max - min)) + min;
    }

    private static int leftNeighbour() {
        return ((rank + size) - 1) % size;
    }

    private static int rightNeighbour() {
        return (rank + 1) % size;
    }

    public enum ForkState {
        NON_EXISTANT, ASKED_BUT_NO_ANSWER, DIRTY, CLEAN
    }

    public enum Side {
        LEFT, RIGHT
    }
}