#!/usr/bin/python

import sys, re, os, subprocess, time, math

# Yes, we're still at python 2.6. Deal with it.
import getopt

def main():

    startTime = int(time.time())

    optList, bs = getopt.getopt(sys.argv[1:], '', [
        'help',
        'debug',
        'type=',
        'openmvg=',
        'openmvs=',
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
        'oopenmvs',
        'grotavg=',
        'gtransavg=',
        'descmethod=',
        'densify',
        'densifyonly',
        'cudarefine',
        'rtfactor=',
        'dnfviews=',
        'dnviews',
        'drlevel=',
        'rmpdistance=',
        'output-obj',
        'rscales=',
        'opmvs'
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
        refineMeshOptions = []
        textureMeshOptions = []
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

#            matchesDirectory = os.path.join(outputDirectory, "matches")
#            reconstructionDirectory = os.path.join(outputDirectory, "reconstruction_global")
        matchesDirectory = os.path.join(outputDirectory, "matches")
        reconstructionDirectory = os.path.join(outputDirectory, "reconstruction_global")
        MVSDirectory = os.path.join(outputDirectory, "omvs")

        # Generic linux paths
        scriptLocation = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        if os.path.exists("/opt/openmvg/share/openMVG"):

            camera_file_params = "/opt/openmvg/share/openMVG/sensor_width_camera_database.txt"

            # Binary locations:
            openmvgBinaries = "/opt/openmvg/bin"
            openmvsBinaries = "/opt/openmvs/bin/OpenMVS"
            cmvsBinaries = "/opt/cmvs/bin"

        else:
            CAMERA_SENSOR_WIDTH_DIRECTORY = os.path.join(scriptLocation, "sensor_database")
            camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")
            # Binary locations:
            openmvgBinaries = os.path.join(scriptLocation, "bin", "openmvg-20170328")
            openmvsBinaries = os.path.join(scriptLocation, "bin", "openmvs")
            cmvsBinaries = os.path.join(scriptLocation, "bin", "cmvs", "bin")

        if getOpt.findKey("--openmvg"):
            openmvgBinaries = getOpt.optValue
        if getOpt.findKey("--openmvs"):
            openmvsBinaries = getOpt.optValue

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

        if getOpt.findKey("--drlevel"):
            densifyPointCloudOptions += ['--resolution-level', getOpt.optValue]

        # ReconstructMesh
        if getOpt.findKey("--rtfactor"):
            reconstructMeshOptions += ['--thickness-factor', getOpt.optValue]

        if getOpt.findKey("--rmpdistance"):
            reconstructMeshOptions += ['--min-point-distance', getOpt.optValue]
        
        if getOpt.findKey("--output-obj"):
            reconstructMeshOptions += ['--export-type', 'obj']

        # Refine Mesh
        if getOpt.findKey("--output-obj"):
            refineMeshOptions += ['--export-type', 'obj']

        if getOpt.findKey("--rscales"):
            refineMeshOptions += ['--scales', getOpt.optValue]

        # Texture Mesh
        if getOpt.findKey("--output-obj"):
            textureMeshOptions += ['--export-type', 'obj']


        if debug == False:
            # Create the ouput/matches folder if not present
            if not os.path.exists(outputDirectory):
                os.mkdir(outputDirectory)
            if not os.path.exists(matchesDirectory):
                os.mkdir(matchesDirectory)
            if not os.path.exists(reconstructionDirectory):
                os.mkdir(reconstructionDirectory)

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

        if getOpt.findKey("--opmvs"):

            commands.append([
                "Convert OpenMVG project to PMVS",
                [os.path.join(openmvgBinaries, "openMVG_main_openMVG2PMVS"), "-i", os.path.join(reconstructionDirectory, "sfm_data.bin"), "-o", outputDirectory]
            ])

            if os.name == "posix":
                commands.append([
                    "Run PMVS using default settings",
                    [os.path.join(cmvsBinaries, "pmvs2"), os.path.join(outputDirectory, "PMVS/"), "pmvs_options.txt"]
                ])

            else:

                commands.append([
                    "Run PMVS using default settings",
                    [os.path.join(cmvsBinaries, "pmvs2"), os.path.join(outputDirectory, "PMVS\\"), "pmvs_options.txt"]
                ])

            # ....but how the hell do you convert pmvs/cmvs to openmvs?


        if getOpt.findKey("--oopenmvs"):

            sceneFileName = ['scene']

            commands.append([
                "Convert OpenMVG project to OpenMVS",
                [os.path.join(openmvgBinaries, "openMVG_main_openMVG2openMVS"), "-i", os.path.join(reconstructionDirectory, "sfm_data.bin"), "-o", os.path.join(MVSDirectory, "scene.mvs"), "-d", MVSDirectory]
            ])

            # Do densifyPointCloud or not
            if getOpt.findKey("--densify") or getOpt.findKey("--densifyonly"):
                commands.append([
                    "Densify point cloud",
                    [os.path.join(openmvsBinaries, "DensifyPointCloud"), "scene.mvs", "-w", MVSDirectory, "-v", "3"] + densifyPointCloudOptions
                ])
                sceneFileName.append("dense")

            if not getOpt.findKey("--densifyonly"):

                mvsFileName = '_'.join(sceneFileName) + ".mvs"
                commands.append([
                    "Reconstruct mesh",
                    [os.path.join(openmvsBinaries, "ReconstructMesh"), mvsFileName, "-w", MVSDirectory, "-v", "3"] + reconstructMeshOptions
                ])
                sceneFileName.append("mesh")


                mvsFileName = '_'.join(sceneFileName) + ".mvs"
                if getOpt.findKey("--cudarefine"):
                    commands.append([
                        "Refine mesh using CUDA",
                        [os.path.join(openmvsBinaries, "RefineMeshCUDA"), mvsFileName, "-w", MVSDirectory, "-v", "3"] + refineMeshOptions
                    ])
                else:
                    commands.append([
                        "Refine mesh",
                        [os.path.join(openmvsBinaries, "RefineMesh"), mvsFileName, "-w", MVSDirectory, "-v", "3"] + refineMeshOptions
                    ])
                sceneFileName.append("refine")


                mvsFileName = '_'.join(sceneFileName) + ".mvs"
                commands.append([
                    "Texture mesh",
                    [os.path.join(openmvsBinaries, "TextureMesh"), mvsFileName, "-w", MVSDirectory, "-v", "3", "--empty-color", "0"] + textureMeshOptions
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
    For instructions see https://github.com/rennu/dpg/blob/master/readme.md
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
