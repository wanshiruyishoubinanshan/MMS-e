# MMS-e: Benchmarking the Resilience of Large Multimodal Models to Visual Scrambling
***
## Benchmark Examples
![Demo1](imgs/lab1.jpeg)
(1) Patchwise Question Answering (Figure~\ref{lab1 data}): Divide the images into 2x2, 4x4, and 8x8 patches, then shuffle all the patches, and measure the ability of LMMs to answer questions about these images. 
![Demo2](imgs/lab2.jpeg)
(2) Reconstruction task (Figure~\ref{lab2 data}): Let LMMs reconstruct the order of shuffled patches based on the image' s caption, and let LMMs reconstruct the shuffled caption based on the image. 
![Demo3](imgs/lab3.jpeg)
(3) Fixed Patch Question Answering (Figure~\ref{lab3 data}): Divide the image into 4x4 patches, randomly fix some of the patches, and let LMMs answer questions based on the image.
