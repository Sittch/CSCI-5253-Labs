
|  Method 	| Local  	| Same-Zone  	|  Different Region 	|
|---	|---	|---	|---	
|   REST add	|  2.747 ms 	|  3.195 ms 	| 288.219 ms 	|
|   gRPC add	|  0.407 ms 	|  0.608 ms 	| 146.054 ms   	|
|   REST rawimg	|  5.365 ms 	| 7.956 ms  	| 1264.280 ms  	|
|   gRPC rawimg	|  12.620 ms     | 9.926 ms  	| 199.539 ms  	|
|   REST dotproduct	|  3.504 ms 	| 4.163 ms  	| 289.879 ms 	|
|   gRPC dotproduct	|  0.582 ms 	| 0.680 ms  	| 145.253 ms   	|
|   REST jsonimg	|  68.800 ms 	| 74.359 ms  	| 1360.678 ms  	|
|   gRPC jsonimg	|  25.934 ms     | 24.973 ms  	| 228.664 ms  	|
|   PING        | 0.046 ms      | 0.249 ms     | 145 ms      |

You should measure the basic latency  using the `ping` command - this can be construed to be the latency without any RPC or python overhead.

You should examine your results and provide a short paragraph with your observations of the performance difference between REST and gRPC. You should explicitly comment on the role that network latency plays -- it's useful to know that REST makes a new TCP connection for each query while gRPC makes a single TCP connection that is used for all the queries.

gRPC is much faster overall than REST in nearly every category. The only exception occurs in rawImage using Local or Same-Zone transfers. It seems than using gRPC may be ovekill in some instances, or REST's creating a new TCP connection for every query provides enough of an advantage due to the very low latency of these two modes. When latency spikes across regions, suddenly the situation is inverted and gRPC obtains the widest latency advantage of any of these categories. 
