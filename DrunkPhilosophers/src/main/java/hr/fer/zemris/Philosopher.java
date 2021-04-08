package hr.fer.zemris;

import mpi.MPI;
import mpi.Status;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;

import static hr.fer.zemris.Philosopher.ForkState.*;
import static hr.fer.zemris.Philosopher.Side.LEFT;
import static hr.fer.zemris.Philosopher.Side.RIGHT;
import static java.lang.Boolean.FALSE;
import static java.lang.Math.random;
import static java.lang.Math.round;
import static java.lang.Thread.sleep;
import static java.util.Map.of;

public class Philosopher {

    private static final char[] EMPTY = {};
    private static final int CHECK_FOR_REQUEST_INTERVAL = 500;
    private static final int GRANT_FORK = 69, BEG_FOR_FORK = 420;

    private static final Map<Side, ForkState> FORKS = new EnumMap<>(of(LEFT, DIRTY, RIGHT, NON_EXISTENT));
    private static final Map<Side, Boolean> REQUESTS = new EnumMap<>(of(LEFT, FALSE, RIGHT, FALSE));
    private static final Map<Side, Integer> NEIGHBOURS = new HashMap<>();

    private static int rank;

    public static void main(String[] args) throws InterruptedException {
        MPI.Init(args);
        initEnvironment();

        think();
        System.out.println(rank + " WANTS TO EAT");
        Side missingFork = getMissingForkSide();
        while (missingFork != null) {
            if (FORKS.get(missingFork) == NON_EXISTENT) {
                System.out.println(rank + " WANTS " + missingFork);

                MPI.COMM_WORLD.Isend(EMPTY, 0, 0, MPI.CHAR, NEIGHBOURS.get(missingFork), BEG_FOR_FORK);
                FORKS.put(missingFork, ASKED_BUT_NO_ANSWER);
            }

            var message = MPI.COMM_WORLD.Recv(EMPTY, 0, 0, MPI.CHAR, MPI.ANY_SOURCE, MPI.ANY_TAG);
            var isReceivedFork = responseToMessage(message);
            if (isReceivedFork)
                missingFork = getMissingForkSide();
        }
        eat();
        respondIfNeeded();

        while (true) {
            for (var neighbour : NEIGHBOURS.values()) {
                if (MPI.COMM_WORLD.Iprobe(neighbour, BEG_FOR_FORK) != null)
                    responseToMessage(MPI.COMM_WORLD.Probe(neighbour, BEG_FOR_FORK));
            }
            if (Math.random() > 1) break;
        }

        MPI.Finalize();
    }

    private static void respondIfNeeded() {
        for (var side : Side.values()) {
            if (!REQUESTS.get(side)) continue;
            FORKS.put(side, NON_EXISTENT);
//            System.out.println(rank + " DELAYED REPLY " + side);
            MPI.COMM_WORLD.Isend(EMPTY, 0, 0, MPI.CHAR, NEIGHBOURS.get(side), GRANT_FORK);
            REQUESTS.put(side, false);
        }
    }

    private static Side getMissingForkSide() {
        if (missesFork(LEFT)) return LEFT;
        if (missesFork(RIGHT)) return RIGHT;
        return null;
    }

    private static boolean missesFork(Side side) {
        return FORKS.get(side) == NON_EXISTENT || FORKS.get(side) == ASKED_BUT_NO_ANSWER;
    }

    private static boolean responseToMessage(Status message) {
        var neighbour = getNeighbour(message.source);
        if (message.tag == GRANT_FORK) {
            System.out.println(rank + " GETS " + neighbour + " FORK");
            FORKS.put(neighbour, CLEAN);
            return true;
        }
        if (message.tag == BEG_FOR_FORK) {
            if (FORKS.get(neighbour) == CLEAN) {
                System.out.println(rank + " NOTICE REQUEST " + neighbour);
                REQUESTS.put(neighbour, true);
            } else if (FORKS.get(neighbour) == DIRTY) {
                System.out.println(rank + " INSTANT GRANT " + neighbour);
                FORKS.put(neighbour, NON_EXISTENT);
                MPI.COMM_WORLD.Isend(EMPTY, 0, 0, MPI.CHAR, message.source, GRANT_FORK);
            }
        }
        return false;
    }

    private static Side getNeighbour(int source) {
        if (source == NEIGHBOURS.get(LEFT)) return LEFT;
        if (source == NEIGHBOURS.get(RIGHT)) return RIGHT;
        return null;
    }

    private static void eat() {
        System.out.println(rank + " EATING!");
        FORKS.put(LEFT, DIRTY);
        FORKS.put(RIGHT, DIRTY);
    }

    private static void think() throws InterruptedException {
        System.out.println(rank + " THINKING");
        var sleepLen = randomNumberInRange();
        for (int i = 0; i < sleepLen; i += CHECK_FOR_REQUEST_INTERVAL) {
            sleep(CHECK_FOR_REQUEST_INTERVAL);
            for (var neighbour : NEIGHBOURS.values()) {
                if (MPI.COMM_WORLD.Iprobe(neighbour, BEG_FOR_FORK) != null)
                    responseToMessage(MPI.COMM_WORLD.Probe(neighbour, BEG_FOR_FORK));
            }
        }
    }

    private static void initEnvironment() {
        rank = MPI.COMM_WORLD.Rank();
        int size = MPI.COMM_WORLD.Size();

        if (rank == 0) FORKS.put(RIGHT, DIRTY);
        if (rank + 1 == size) FORKS.put(LEFT, NON_EXISTENT);

        NEIGHBOURS.put(RIGHT, ((rank + size) - 1) % size);
        NEIGHBOURS.put(LEFT, (rank + 1) % size);
    }

    private static long randomNumberInRange() {
        return round(random() * (10000 - 1000)) + 1000;
    }

    public enum ForkState {
        NON_EXISTENT, ASKED_BUT_NO_ANSWER, DIRTY, CLEAN
    }

    public enum Side {
        LEFT, RIGHT
    }
}