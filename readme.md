# OpenMVG + OpenMVS Pipeline

Photogrammetry pipeline using [OpenMVG](https://github.com/openMVG/openMVG) and [OpenMVS](https://github.com/cdcseacave/openMVS).

(Also includes [CMVS](https://github.com/pmoulon/CMVS-PMVS) and [COLMAP](https://github.com/colmap/colmap)).

## Installation
Windows:
1. Install Windows Subsystem for Linux (Ubuntu 16.04)
2. Clone repository
3. ```sudo ./build.sh```

Linux (Ubuntu 16.04):
1. Clone repository
2. ```sudo ./build.sh```

Docker:
1. Clone repository
2. ```docker build -t dpg .```
3. ```docker run -v $(pwd):/datasets --rm -it dpg```

## Examples

### Mesh Reconstruction with Textures by using Incremental Structure from Motion
1. Download [example image set](https://github.com/openMVG/ImageDataset_SceauxCastle), open it up in terminal and run the docker image (see above)
2. Run pipeline:


```/opt/dpg/pipeline.py --input /datasets/images --output /datasets/output --sfm-type incremental --geomodel f --run-openmvg --run-openmvs```

3. Open your model for example using meshlab. The model is named "scene_mesh_refine_texture.ply" and it's under $datasets/ImageDataset_SceauxCastle/sfm/mvs directory

You should end up with something like this (press ctrl/cmd-k to disable backface culling) ![Example 1](https://i.imgur.com/CpSs2SE.jpg)

### Dense Mesh Reconstruction with Textures by using Incremental Structure from Motion
1. Download [example image set](https://github.com/openMVG/ImageDataset_SceauxCastle), open it up in terminal and run the docker image (see above)
2. Run pipeline: 

```/opt/dpg/pipeline.py --input /datasets/images --output /datasets/output_dense --sfm-type incremental --geomodel f --run-openmvg --run-openmvs --densify```

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

        --sfm-type [string]
            Select SfM mode from Global SfM or Incremental SfM. Possible values:
            incremental
            global
        
        --run-openmvg
            Run OpenMVG SfM pipeline

        --run-openmvs
            Run OpenMVS MVS pipeline
        
    Optional settings:

        --recompute
            Recompute everything

        --openmvg [path]
            Set OpenMVG install location
        
        --openmvs [path]
            Set OpenMVS install location

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
        
            --matching [string]
                Compute Matches Nearest Matching Method:
                BRUTEFORCEL2: BruteForce L2 matching for Scalar based regions descriptor,
                ANNL2: Approximate Nearest Neighbor L2 matching for Scalar based regions descriptor,
                CASCADEHASHINGL2: L2 Cascade Hashing matching,
                FASTCASCADEHASHINGL2: (default)
                    * L2 Cascade Hashing with precomputed hashed regions, (faster than CASCADEHASHINGL2 but use more memory).

        Incremental SfM:

            --icmodel [int]
                The camera model type that will be used for views with unknown intrinsic
                1: Pinhole
                2: Pinhole radial 1
                3: Pinhole radial 3 (default)
                4: Pinhole radial 3 + tangential 2
                5: Pinhole fisheye

        Global SfM:

            --grotavg [int]
                1: L1 rotation averaging [Chatterjee]
                2: L2 rotation averaging [Martinec] (default)

            --gtransavg [int]
                1: L1 translation averaging [GlobalACSfM]
                2: L2 translation averaging [Kyle2014]
                3: SoftL1 minimization [GlobalACSfM] (default)


    OpenMVS

        --output-obj
            Make OpenMVS output obj instead of ply (default)

        DensifyPointCloud:

            --densify
                Enable dense reconstruction
                Default: Off
            
            --densify-only
                Only densify (duh)

            --dnumviews [int]
                Number of views used for depth-map estimation
                0 all neighbor views available
                Default: 4
        
            --dnumviewsfuse [int]
                Minimum number of images that agrees with an estimate during fusion in order to consider it
                inliner
                Default: 3

            --dreslevel [int]
                How many times to scale down the images before point cloud computation. For better accuracy/speed width
                high resolution images use 2 or even 3
                Default: 1
        
        ReconstructMesh:

            --rcthickness [int]
                ReconstructMesh Thickness Factor
                Default: 2
            
            --rcdistance [int]
                Minimum distance in pixels between the projection of two 3D points to consider them different while
                triangulating (0 to disable). Use to reduce amount of memory used with a penalty of lost detail
                Default: 2
        
        RefineMesh:

            --rmiterations [int]
                Number of RefineMesh iterations
                Default: 3

            --rmlevel [int]
                Times to scale down the images before mesh refinement
                Default: 0

            --rmcuda
                Use CUDA version of RefineMesh binary (will fall back the executable is not found)
        
        Texture Mesh:

            --txemptycolor [int]
                Color of surfaces OpenMVS TextureMesh is unable to texture.
                Default: 0 (black)
        
