# OpenMVG + OpenMVS Pipeline in Docker

Basic photogrammetry pipeline using [OpenMVG](https://github.com/openMVG/openMVG), [OpenMVS](https://github.com/cdcseacave/openMVS) and [Docker](http://www.docker.com/).

## Installation
1. Install docker
2. Get docker image and view help ```docker run --rm spedenaave/dpg:latest --help```
3. On macos and windows: Open up docker settings and tweak the amount of resources it is allowed to use. The default settings are too low...

## Running the pipeline
On macos / linux:

```docker run --rm -v `pwd`:/datasets spedenaave/dpg [pipeline arguments]```
* `--rm` removes the container after the reconstruct has finished.
* ```-v `pwd`:/datasets ``` mounts current working directory to /datasets so that the script is able to access your hosts filesystem

Windows:

```docker run --rm -v `pwd`:/datasets spedenaave/dpg [pipeline arguments]```
* `--rm` removes the container after the reconstruct has finished.
* `-v "%cd%":/datasets` mounts current working directory to /datasets so that the script is able to access your hosts filesystem
* **Note: With files and directories use forward slashes (/) instead of slashes (\\)**

**Note**: 

## Examples

### Mesh Reconstruction with Textures by using Incremental Structure from Motion
1. Download [example image set](https://github.com/openMVG/ImageDataset_SceauxCastle) to ~/datasets directory and open it up in terminal.
2. Run pipeline:

macos / linux:

```docker run --rm -v `pwd`:/datasets spedenaave/dpg --input ImageDataset_SceauxCastle/images --output ImageDataset_SceauxCastle/sfm --type incremental --geomodel f --oopenmvs```

Windows:

```docker run --rm -v "%cd%":/datasets spedenaave/dpg --input ImageDataset_SceauxCastle/images --output ImageDataset_SceauxCastle/sfm --type incremental --geomodel f --oopenmvs```

3. Open your model for example using meshlab. The model is named "scene_mesh_refine_texture.ply" and it's under $datasets/ImageDataset_SceauxCastle/sfm/mvs directory

You should end up with something like this (press ctrl/cmd-k to disable backface culling) ![Example 1](https://i.imgur.com/CpSs2SE.jpg)

### Dense Mesh Reconstruction with Textures by using Incremental Structure from Motion
1. Download [example image set](https://github.com/openMVG/ImageDataset_SceauxCastle) to ~/datasets directory and open it up in terminal.
2. Run pipeline

macos / linux: 

```docker run --rm -v `pwd`:/datasets spedenaave/dpg --input ImageDataset_SceauxCastle/images --output ImageDataset_SceauxCastle/mvs_dense --type incremental --geomodel f --oopenmvs --densify```

Windows:

```docker run --rm -v "%cd%":/datasets spedenaave/dpg --input ImageDataset_SceauxCastle/images --output ImageDataset_SceauxCastle/mvs_dense --type incremental --geomodel f --oopenmvs --densify```
3. Open your model for example using meshlab. The model is named "scene_dense_mesh_refine_texture.ply" and it's under $datasets/ImageDataset_SceauxCastle/sfm_dense/mvs directory

The end result should look something like this ![Example 2](https://i.imgur.com/lVerEpa.jpg)

## Pipeline Options

    General Options:

        --help
            Print this text

        --debug
            Print commands and exit

        --input [directory]
            Image input directory

        --output [directory]
            Output directory

        --type [string]
            Select SfM mode from Global SfM or Incremental SfM. Possible values:
            incremental
            global
        
        --oopenmvs
            Export project to OpenMVS
        
        --omeshlab
            Export project to Meshlab

    Optional settings:

        --recompute
            Recompute everything

    OpenMVG

        Image Listing:

            --cgroup
                Each view have it's own camera intrinsic parameters

            --flength [float]
                If your camera is not listed in the camera sensor database, you can set pixel focal length here.
                The value can be calculated by max(width-pixels, height-pixels) * focal length(mm) / Sensor width

            --cmodel [int]
                Camera model:
                1: Pinhole
                2: Pinhole Radial 1
                3: Pinhole Radial 3 (default)
                4: Pinhole brown
                5: Pinhole with a simple Fish-eye distortion

        Compute Features:

            --descmethod [string]
                Method to describe an image:
                    SIFT (default)
                    AKAZE_FLOAT
                    AKAZE_MLDB

            --dpreset [string]
                Used to control the Image_describer configuration
                    NORMAL
                    HIGH
                    ULTRA

        Compute Matches:

            --ratio [float]
                Nearest Neighbor distance ratio (smaller is more restrictive => Less false positives)
                Default: 0.8

            --geomodel [char]
                Compute Matches geometric model:
                f: Fundamental matrix filtering (default)
                    For Incremental SfM
                e: Essential matrix filtering
                    For Global SfM
                h: Homography matrix filtering
                    For datasets that have same point of projection
        
            --nmatching [string]
                Compute Matches Nearest Matching Method:
                BRUTEFORCEL2: BruteForce L2 matching for Scalar based regions descriptor,
                ANNL2: Approximate Nearest Neighbor L2 matching for Scalar based regions descriptor,
                CASCADEHASHINGL2: L2 Cascade Hashing matching,
                FASTCASCADEHASHINGL2: (default)
                    * L2 Cascade Hashing with precomputed hashed regions, (faster than CASCADEHASHINGL2 but use more memory).

        Incremental SfM

            --icmodel [int]
                The camera model type that will be used for views with unknown intrinsic
                1: Pinhole
                2: Pinhole radial 1
                3: Pinhole radial 3 (default)
                4: Pinhole radial 3 + tangential 2
                5: Pinhole fisheye

        Global SfM

            --grotavg [int]
                1: L1 rotation averaging [Chatterjee]
                2: L2 rotation averaging [Martinec] (default)

            --gtransavg [int]
                1: L1 translation averaging [GlobalACSfM]
                2: L2 translation averaging [Kyle2014]
                3: SoftL1 minimization [GlobalACSfM] (default)


    OpenMVS

        DensifyPointCloud

            --densify
                Enable dense reconstruction
                Default: Off

            --dnviews
                Number of views used for depth-map estimation
                0 all neighbor views available
                Default: 4
        
            --dnfviews
                Minimum number of images that agrees with an estimate during fusion in order to consider it
                inliner
                Default: 3

            --drlevel
                How many times to scale down the images before point cloud computation. For better accuracy/speed width
                high resolution images use 2 or even 3
                Default: 1
        
        ReconstructMesh

            --rtfactor
                ReconstructMesh Thickness Factor
                Default: 2
            
            --rmpdistance
                Minimum distance in pixels between the projection of two 3D points to consider them different while
                triangulating (0 to disable). Use to reduce amount of memory used with a penalty of lost detail
                Default: 2

