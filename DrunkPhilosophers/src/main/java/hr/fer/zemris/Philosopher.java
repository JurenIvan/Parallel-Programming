package hr.fer.zemris;

import mpi.MPI;

public class Philosopher {

    public static void main(String[] args) {
        MPI.Init(args);
        System.out.println("hello");

        int rank = MPI.COMM_WORLD.Rank();
        int size = MPI.COMM_WORLD.Size();

        System.out.println(rank + "  " + size);

        MPI.Finalize();
    }
}

/*
comp2@comp2:~/Desktop/mpj-user-sss$ javac -cp /home/comp2/Desktop/mpj-v0_44/lib/mpj.jar hr.fer.zemris.MPI_Scatter_Gather_Demo.java

comp2@comp2:~/Desktop/mpj-user-sss$ mpjrun.sh -np 4 hr.fer.zemris.MPI_Scatter_Gather_Demo

MPJ Express (0.44) is started in the multicore configuration
0 0 0 0 1 1 1 1 2 2 2 2 3 3 3 3
*/
