#!/usr/bin/python

import getopt, sys, re, os, subprocess, time, math

def main():

    startTime = int(time.time())

    optList, bs = getopt.getopt(sys.argv[1:], '', [
        'help',
        'debug',
        'type=',
        'openmvg=',
        'openmvs=',
        'meshlab=',
        'cgroup',
        'flength=',
        'ratio=',
        'geomodel=',
        'nmatching=',
        'input=',
        'output=',
        'cmodel=',
        'icmodel=',
        'dpreset=',
        'recompute',
        'upright',
        'omeshlab',
        'oopenmvs',
        'grotavg=',
        'gtransavg=',
        'descmethod=',
        'densify',
        'cudarefine',
        'tfactor=',
        'dnfviews=',
        'dnviews'
    ])

    getOpt = optFinder(optList)

    if getOpt.findKey("--help"):
        printHelp()
        sys.exit()

    if getOpt.findKey("--type") and getOpt.findKey("--input") and getOpt.findKey("--output"):

        imageListingOptions = []
        computeFeaturesOptions = []
        computeMatchesOptions = []
        incrementalSFMOptions = []
        globalSFMOptions = []
        dataColorOptions = []
        structureFromPosesOptions = []
        densifyPointCloudOptions = []
        reconstructMeshOptions = []
        commands = []


        # Mandatory
        inputDirectory = False
        if getOpt.findKey("--input"):
            inputDirectory = getOpt.optValue
        outputDirectory = False
        if getOpt.findKey("--output"):
            outputDirectory = getOpt.optValue
        pipelineType = False
        if getOpt.findKey("--type"):
            pipelineType = getOpt.optValue

        # Set directories

        # Detect docker

        scriptLocation = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        if os.path.exists("/opt/openmvg/share/openMVG"):

            outputDirectory = os.path.join("/datasets", outputDirectory)
            inputDirectory = os.path.join("/datasets", inputDirectory)

            camera_file_params = "/opt/openmvg/share/openMVG/sensor_width_camera_database.txt"

            matchesDirectory = os.path.join(outputDirectory, "matches")
            reconstructionDirectory = os.path.join(outputDirectory, "reconstruction_global")
            MVSDirectory = os.path.join(outputDirectory, "mvs")
            meshlabDirectory = os.path.join(outputDirectory, "meshlab")
            # Binary locations:

            openmvgBinaries = "/opt/openmvg/bin"
            openmvsBinaries = "/opt/openmvs/bin/OpenMVS"
            meshlabBinaries = os.path.join(scriptLocation, "bin", "meshlab")

        else:
            CAMERA_SENSOR_WIDTH_DIRECTORY = os.path.join(scriptLocation, "sensor_database")
            camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")
            matchesDirectory = os.path.join(outputDirectory, "matches")
            reconstructionDirectory = os.path.join(outputDirectory, "reconstruction_global")
            MVSDirectory = os.path.join(outputDirectory, "mvs")
            meshlabDirectory = os.path.join(outputDirectory, "meshlab")
            # Binary locations:
            openmvgBinaries = os.path.join(scriptLocation, "bin", "openmvg-develop")
            openmvsBinaries = os.path.join(scriptLocation, "bin", "openmvs")
            meshlabBinaries = os.path.join(scriptLocation, "bin", "meshlab")


        if getOpt.findKey("--openmvg"):
            openmvgBinaries = getOpt.optValue
        if getOpt.findKey("--openmvs"):
            openmvsBinaries = getOpt.optValue
        if getOpt.findKey("--meshlab"):
            meshlabBinaries = getOpt.optValue

        # Debug
        debug = False
        if getOpt.findKey("--debug"):
            debug = True

        # Recompute everything
        if getOpt.findKey("--recompute"):
            computeFeaturesOptions += ["-f", "1"]
            computeMatchesOptions += ["-f", "1"]

        # Image Listing
        if getOpt.findKey("--flength"):
            imageListingOptions += ['-f', getOpt.optValue]

        if getOpt.findKey("--cmodel"):
            imageListingOptions += ['-c', getOpt.optValue]

        if getOpt.findKey("--cgroup"):
            imageListingOptions += ['-g', '0']

        # Compute Features
        if getOpt.findKey("--descmethod"):
            computeFeaturesOptions += ['-m', getOpt.optValue.upper()]

        if getOpt.findKey("--dpreset"):
            computeFeaturesOptions += ['-p', getOpt.optValue.upper()]

        if getOpt.findKey("--upright"):
            computeFeaturesOptions += ['-u', '1']

        # Compute Matches
        if getOpt.findKey("--ratio"):
            computeMatchesOptions += ['-r', getOpt.optValue]

        if getOpt.findKey("--geomodel"):
            computeMatchesOptions += ['-g', getOpt.optValue]
        
        if getOpt.findKey("--nmatching"):
            computeMatchesOptions += ['-n', getOpt.optValue.upper()]

        # Incremental SfM
        if getOpt.findKey("--icmodel"):
            incrementalSFMOptions += ['-c', getOpt.optValue]

        # Global SfM
        if getOpt.findKey("--grotavg"):
            globalSFMOptions += ['-r', getOpt.optValue]

        if getOpt.findKey("--gtransavg"):
            globalSFMOptions += ['-t', getOpt.optValue]
        
        # DensifyPointCloud
        if getOpt.findKey("--dnfviews"):
            densifyPointCloudOptions += ['--number-views-fuse', getOpt.optValue]

        if getOpt.findKey("--dnviews"):
            densifyPointCloudOptions += ['--number-views', getOpt.optValue]

        # ReconstructMesh
        if getOpt.findKey("--tfactor"):
            reconstructMeshOptions += ['--thickness-factor', getOpt.optValue]

        if debug == False:
            # Create the ouput/matches folder if not present
            if not os.path.exists(outputDirectory):
                os.mkdir(outputDirectory)
            if not os.path.exists(matchesDirectory):
                os.mkdir(matchesDirectory)
            if not os.path.exists(reconstructionDirectory):
                os.mkdir(reconstructionDirectory)

            if getOpt.findKey("--omeshlab"):
                if not os.path.exists(meshlabDirectory):
                    os.mkdir(meshlabDirectory)

            if getOpt.findKey("--oopenmvs"):
                if not os.path.exists(MVSDirectory):
                    os.mkdir(MVSDirectory)


        # Create commands
        commands.append([
            "Instrics analysis",
            [os.path.join(openmvgBinaries, "openMVG_main_SfMInit_ImageListing"),  "-i", inputDirectory, "-o", matchesDirectory, "-d", camera_file_params] + imageListingOptions
        ])

        commands.append([
            "Compute features",
            [os.path.join(openmvgBinaries, "openMVG_main_ComputeFeatures"),  "-i", os.path.join(matchesDirectory, "sfm_data.json"), "-o", matchesDirectory, "-m", "SIFT"] + computeFeaturesOptions
        ])

        commands.append([
            "Compute matches",
            [os.path.join(openmvgBinaries, "openMVG_main_ComputeMatches"),  "-i", os.path.join(matchesDirectory, "sfm_data.json"), "-o", matchesDirectory] + computeMatchesOptions
        ])

        # Select pipeline type
        if pipelineType == "global":

            commands.append([
                "Do incremental/sequential reconstruction",
                [os.path.join(openmvgBinaries, "openMVG_main_GlobalSfM"),  "-i", os.path.join(matchesDirectory, "sfm_data.json"), "-m", matchesDirectory, "-o", reconstructionDirectory] + globalSFMOptions
            ])
        elif pipelineType == "incremental":
            commands.append([
                "Do incremental/sequential reconstruction",
                [os.path.join(openmvgBinaries, "openMVG_main_IncrementalSfM"),  "-i", os.path.join(matchesDirectory, "sfm_data.json"), "-m", matchesDirectory, "-o", reconstructionDirectory] + incrementalSFMOptions
            ])
        else:
            print "Incorrect pipeline type -> Exit"
            sys.exit()

        # What to do after openmvg has finished?
        if getOpt.findKey("--omeshlab"):

            commands.append([
                "Convert OpenMVG project to Meshlab",
                [os.path.join(openmvgBinaries, "openMVG_main_openMVG2MESHLAB"), "-i", os.path.join(reconstructionDirectory, "sfm_data.bin"), "-p", reconstructionDirectory, "-o", meshlabDirectory]
            ])

        if getOpt.findKey("--oopenmvs"):

            sceneFileName = ['scene']

            commands.append([
                "Convert OpenMVG project to OpenMVS",
                [os.path.join(openmvgBinaries, "openMVG_main_openMVG2openMVS"), "-i", os.path.join(reconstructionDirectory, "sfm_data.bin"), "-o", os.path.join(MVSDirectory, "scene.mvs"), "-d", MVSDirectory]
            ])

            # Do densifyPointCloud or not
            if getOpt.findKey("--densify"):
                commands.append([
                    "Densify point cloud",
                    [os.path.join(openmvsBinaries, "DensifyPointCloud"), "scene.mvs", "-w", MVSDirectory, "-v", "3"] + densifyPointCloudOptions
                ])
                sceneFileName.append("dense")

            mvsFileName = '_'.join(sceneFileName) + ".mvs"
            commands.append([
                "Reconstruct mesh",
                [os.path.join(openmvsBinaries, "ReconstructMesh"), mvsFileName, "-w", MVSDirectory, "-v", "3"]
            ])
            sceneFileName.append("mesh")


            mvsFileName = '_'.join(sceneFileName) + ".mvs"
            if getOpt.findKey("--cudarefine"):
                commands.append([
                    "Refine mesh using CUDA",
                    [os.path.join(openmvsBinaries, "RefineMeshCUDA"), mvsFileName, "-w", MVSDirectory, "-v", "3"]
                ])
            else:
                commands.append([
                    "Refine mesh",
                    [os.path.join(openmvsBinaries, "RefineMesh"), mvsFileName, "-w", MVSDirectory, "-v", "3"]
                ])
            sceneFileName.append("refine")


            mvsFileName = '_'.join(sceneFileName) + ".mvs"
            commands.append([
                "Texture mesh",
                [os.path.join(openmvsBinaries, "TextureMesh"), mvsFileName, "-w", MVSDirectory, "-v", "3", "--empty-color", "0"]
            ])
        
        for instruction in commands:

            if debug == True:
                print ' '.join(instruction[1])
            if debug == False:
                print ("\n\n" + str(instruction[0]))
                print ("============================================================================================")
                print "Executing: " + ' '.join(instruction[1])
                sp = subprocess.Popen( instruction[1] )
                sp.wait()
                sp.communicate()
                if sp.returncode != 0:
                    print "Process did not exit correctly (return code != 0). Giving up :("
                    sys.exit(1)

        # Output pipeline total completion time
        endTime = int(time.time())
        timeDifference = endTime - startTime
        hours = math.floor(timeDifference / 60 / 60)
        minutes = math.floor((timeDifference - hours * 60 * 60) / 60)
        seconds = math.floor(timeDifference - (hours * 60 * 60 + minutes * 60))

        print "\n\nUsed time: " + str(int(hours)) + "h " + str(int(minutes)) + "m " + str(int(seconds)) + "s"

    else:
        print "Missing some of mandatory parameters: --type, --input and --output"
        print "Use --help to see usage instructions"
        sys.exit()



def printHelp():
    print """

    Usage: pipeline.py --type [incremental|global] --openmvg [directory] --openmvs [directory] [options] [input directory] [output directory]

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

        --openmvg [directory]
            Location of OpenMVG binaries
            default: /path/to/script/../bin/openmvg
        
        --openmvs [directory]
            Location of OpenMVS binaries
            default: /path/to/script/../bin/openmvs

        --meshlab [directory]
            Location of Meshlab binaries
            default: /path/to/script/../bin/meshlab

        --recompute
            Recompute everything

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
            --densify
                Do DensifyPointCloud

            --dnviews
                Number of views used for depth-map estimation
                0 all neighbor views available
                Default: 4
            
            --dnfviews
                Minimum number of images that agrees with an estimate during fusion in order to consider it
                inliner
                Default: 3
            
            --tfactor
                ReconstructMesh Thickness Factor

            --cudarefine
                Use CUDA version of RefineMesh

    """



class optFinder:
    optList = []
    optValue = "" 

    def __init__(self, *optList):
        self.optList = optList

    def findKey(self, optKey):
        self.optValue = ""


        for oKey, oValue in self.optList[0]:
            if oKey == optKey:
                self.optValue = oValue
                return True

        return False


main()
