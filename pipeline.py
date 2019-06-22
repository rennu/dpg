#!/usr/bin/python

import argparse, os, subprocess, time, math, sys, errno

MVSDirectory = ''
outputDirectory = ''

def createParser():
    parser = argparse.ArgumentParser(description='OpenMVG/OpenMVS pipeline')
    parser._action_groups.pop()

    required = parser.add_argument_group('Required arguments')
    required.add_argument('--input',
        help='Input images folder',
        required=True)
    required.add_argument('--output', 
        help='Output path',
        required=True)

    required.add_argument('--sfm-type',
        help='Select SfM type: global or incremental',
        choices=['global', 'incremental'],
        required=True)

    pipelines = parser.add_argument_group('Pipelines to run (min. 1 required)')
    pipelines.add_argument('--run-openmvg',
        action='store_true',
        help='Run OpenMVG pipeline')
    pipelines.add_argument('--run-openmvs',
        action='store_true',
        help='Run OpenMVS pipeline')

    optional = parser.add_argument_group('Optional arguments')
    optional.add_argument('--debug',
        action='store_true',
        help='Print commands without executing them')
    optional.add_argument('--recompute',
        action='store_true',
        help='Recompute everything')
    optional.add_argument('--openmvg',
        help='Location of openmvg. Default: /opt/openmvg')
    optional.add_argument('--openmvs',
        help='Location of openmvs. Default: /opt/openmvs')

    openmvg = parser.add_argument_group('OpenMVG')
    openmvg.add_argument('--colorize',
        action='store_true',
        help='Create colorized sparse pointcloud')

    imageListing = parser.add_argument_group('OpenMVG Image Listing')
    imageListing.add_argument('--cgroup',
        action='store_true',
        help='Each view has it\'s own camera intrisic parameters')
    imageListing.add_argument('--flength',
        type=int,
        help='If your camera is not listed in the camera sensor database, you can set pixel focal length here. The value can be calculated by max(width-pixels, height-pixels) * focal length(mm) / Sensor width')
    imageListing.add_argument('--cmodel', type=int,
        help='Camera model: 1. Pinhole 2. Pinhole Radial 1 3. Pinhole Radial 3 (Default) 4. Pinhole Brown 5. Pinhole with a Simple Fish-eye Distortion',
        choices=[1, 2, 3, 4, 5])

    computeFeature = parser.add_argument_group('OpenMVG Compute Features')
    computeFeature.add_argument('--descmethod',
        type=str, 
        help='Method to describe and image. Default: SIFT', 
        choices=['SIFT', 'AKAZE_FLOAT', 'AKAZE_MLDB'])
    computeFeature.add_argument('--dpreset',
        help='Used to control the Image_describer configuration. Default: NORMAL',
        choices=['NORMAL', 'HIGH', 'ULTRA'])
    computeFeature.add_argument('--upright',
        help='Use upright feature or not. 0 (default) 1: Extract upright feature')

    computeMatches = parser.add_argument_group('OpenMVG Compute Matches')
    computeMatches.add_argument('--ratio', 
        type=float, 
        help='Nearest Neighbor distance ratio (smaller is more restrictive => Less false positives). Default: 0.8')
    computeMatches.add_argument('--geomodel',
        help='Compute Matches geometric model: f: Fundamental matrix filtering (default) For Incremental SfM e: Essential matrix filtering For Global SfM h: Homography matrix filtering For datasets that have same point of projection',
        choices=['f', 'e', 'h'])
    computeMatches.add_argument('--matching', 
        help='Compute matches nearest matching method. Default: FASTCASCADEHASHINGL2',
        choices=['BRUTEFORCEL2', 'ANNL2', 'CASCADEHASHINGL2', 'FASTCASCADEHASHINGL2'])

    incrementalSfm = parser.add_argument_group('OpenMVG Incremental SfM')
    incrementalSfm.add_argument('--icmodel',
        help='The camera model type that will be used for views with unknown intrinsic: 1. Pinhole 2. Pinhole radial 1 3. Pinhole radial 3 (default) 4. Pinhole radial 3 + tangential 2 5. Pinhole fisheye',
        choices=[1, 2, 3, 4, 5])

    globalSfm = parser.add_argument_group('OpenMVG Global SfM')
    globalSfm.add_argument('--grotavg',
        type=int,
        help='1. L1 rotation averaging [Chatterjee] 2. L2 rotation averaging [Martinec] (default)',
        choices=[1,2]
    )
    globalSfm.add_argument('--gtransavg',
        type=int,
        help='1: L1 translation averaging [GlobalACSfM] 2: L2 translation averaging [Kyle2014] 3: SoftL1 minimization [GlobalACSfM] (default)',
        choices=[1, 2, 3])

    openmvs = parser.add_argument_group('OpenMVS')
    openmvs.add_argument('--output-obj',
        action='store_true',
        help='Output mesh files as obj instead of ply')

    openmvsDensify = parser.add_argument_group('OpenMVS DensifyPointCloud')
    openmvsDensify.add_argument('--densify',
        action='store_true',
        help='Enable dense reconstruction')
    openmvsDensify.add_argument('--densify-only',
        action='store_true',
        help='Densify pointcloud and exit')
    openmvsDensify.add_argument('--dnumviews',
        type=int,
        help='Number of view used for depth-map estimation. 0 for all neighbor views available. Default: 4')
    openmvsDensify.add_argument('--dnumviewsfuse',
        type=int,
        help='Minimum number of images that agrees with an estimate during fusion in order to consider it inliner. Default: 3')
    openmvsDensify.add_argument('--dreslevel',
        type=int,
        help='How many times to scale down the images before point cloud computation. For better accuracy/speed with high resolution images use 2 or even 3. Default: 1')

    openmvsReconstruct = parser.add_argument_group('OpenMVS Reconstruct Mesh')
    openmvsReconstruct.add_argument('--rcthickness',
        type=int,
        help='ReconstructMesh thickness factor. Default: 2')
    openmvsReconstruct.add_argument('--rcdistance',
        type=int,
        help='Minimum distance in pixels between the projection of two 3D points to consider them different while triangulating (0 to disable). Use to reduce amount of memory used with a penalty of lost detail. Default: 2')

    openmvsRefinemesh = parser.add_argument_group('OpenMVS Refine Mesh')
    openmvsRefinemesh.add_argument('--rmiterations',
        type=int,
        help='Number of RefineMesh iterations. Default: 3')
    openmvsRefinemesh.add_argument('--rmlevel',
        type=int,
        help='Times to scale down the images before mesh refinement. Default: 0')
    openmvsRefinemesh.add_argument('--rmcuda',
        action='store_true',
        help='Refine using CUDA version of RefineMesh (if available)')

    openmvsTexture = parser.add_argument_group('OpenMVS Texture Mesh')
    openmvsTexture.add_argument('--txemptycolor',
        default=0,
        type=int,
        help='Color of surfaces OpenMVS TextureMesh is unable to texture. Default: 0 (black)')
    return parser

def createCommands(args):
    imageListingOptions = []
    computeFeaturesOptions = []
    computeMatchesOptions = []
    incrementalSFMOptions = []
    globalSFMOptions = []
    densifyPointCloudOptions = []
    reconstructMeshOptions = []
    refineMeshOptions = []
    textureMeshOptions = []
    commands = []

    inputDirectory = args.input
    global outputDirectory
    outputDirectory = args.output
    matchesDirectory = os.path.join(outputDirectory, 'matches')
    reconstructionDirectory = os.path.join(outputDirectory, 'reconstruction_global')
    global MVSDirectory
    MVSDirectory = os.path.join(outputDirectory, 'omvs')
    openmvgBin = '/opt/openmvg/bin'
    cameraSensorsDB = '/opt/openmvg/share/openMVG/sensor_width_camera_database.txt'
    openmvsBin = '/opt/openmvs/bin/OpenMVS'

    if args.openmvg != None:
        openmvgBin = os.path.join(args.openmvg, 'bin')
        cameraSensorsDB = os.path.join(args.openmvg, 'share', 'openMVG', 'sensor_width_camera_database.txt')

    if args.openmvs != None:
        openmvsBin = os.path.join(args.openmvs, 'bin', 'OpenMVS')

    # Recompute
    if args.recompute:
        computeFeaturesOptions += ['-f', '1']
        computeMatchesOptions += ['-f', '1']

    # OpenMVG SfM Pipeline Type
    pipelineType = args.sfm_type

    # OpenMVG Image Listing
    if args.cgroup:
        imageListingOptions += ['-g', '0']
    if args.flength != None:
        imageListingOptions += ['-f', args.flength]
    if args.cmodel != None:
        imageListingOptions += ['-c', args.cmodel]

    # OpenMVG Compute Features
    if args.descmethod != None:
        computeFeaturesOptions += ['-m', args.descmethod.upper()]
    if args.dpreset != None:
        computeFeaturesOptions += ['-p', args.dpreset.upper()]
    if args.upright:
        computeFeaturesOptions += ['-u', '1']

    # OpenMVG Match Matches
    if args.ratio != None:
        computeMatchesOptions += ['-r', args.ratio]
    if args.geomodel != None:
        computeMatchesOptions += ['-g', args.geomodel]
    if args.matching != None:
        computeMatchesOptions += ['-n', args.matching]

    # OpenMVG Inremental SfM
    if args.icmodel != None:
        incrementalSFMOptions += ['-c', args.icmodel]

    # OpenMVG Global SfM
    if args.grotavg != None:
        globalSFMOptions += ['-r', args.grotavg]
    if args.gtransavg != None:
        globalSFMOptions += ['-t', args.gtransavg]

    # OpenMVS Output Format
    openmvsOutputFormat = []
    if args.output_obj:
        openmvsOutputFormat = ['--export-type', 'obj']

    # OpenMVS Densify Mesh
    if args.dnumviewsfuse != None:
        densifyPointCloudOptions += ['--number-views-fuse', args.dnfviews]
    if args.dnumviews != None:
        densifyPointCloudOptions += ['--number-views', args.dnviews]
    if args.dreslevel != None:
        densifyPointCloudOptions += ['--resolution-level', args.drlevel]
    densifyPointCloudOptions += openmvsOutputFormat

    # OpenMVS Reconstruct Mesh
    if args.rcthickness != None:
        reconstructMeshOptions += ['--thickness-factor', args.rcthickness]
    if args.rcdistance != None:
        reconstructMeshOptions += ['--min-point-distance', args.rcdistance]
    reconstructMeshOptions += openmvsOutputFormat

    # OpenMVS Refine Mesh
    if args.rmiterations != None:
        refineMeshOptions += ['--scales', args.rmiterations]
    if args.rmlevel != None:
        refineMeshOptions += ['--resolution-level', args.rmlevel]
    refineMeshOptions += openmvsOutputFormat

    # OpenMVS Texture Mesh
    if args.txemptycolor != None:
        textureMeshOptions += ['--empty-color', args.txemptycolor]
    textureMeshOptions += openmvsOutputFormat

    # Create commands
    if args.run_openmvg:
        commands.append({
            'title': 'Instrics analysis',
            'command': [os.path.join(openmvgBin, 'openMVG_main_SfMInit_ImageListing'),  '-i', inputDirectory, '-o', matchesDirectory, '-d', cameraSensorsDB] + imageListingOptions
        })

        commands.append({
            'title': 'Compute features',
            'command': [os.path.join(openmvgBin, 'openMVG_main_ComputeFeatures'),  '-i', os.path.join(matchesDirectory, 'sfm_data.json'), '-o', matchesDirectory, '-m', 'SIFT'] + computeFeaturesOptions
        })

        commands.append({
            'title': 'Compute matches',
            'command': [os.path.join(openmvgBin, 'openMVG_main_ComputeMatches'),  '-i', os.path.join(matchesDirectory, 'sfm_data.json'), '-o', matchesDirectory] + computeMatchesOptions
        })

        # Select pipeline type
        if pipelineType == 'global':
            commands.append({
                'title': 'Do Global reconstruction',
                'command': [os.path.join(openmvgBin, 'openMVG_main_GlobalSfM'),  '-i', os.path.join(matchesDirectory, 'sfm_data.json'), '-m', matchesDirectory, '-o', reconstructionDirectory] + globalSFMOptions
            })
        if pipelineType == 'incremental':
            commands.append({
                'title': 'Do incremental/sequential reconstruction',
                'command': [os.path.join(openmvgBin, 'openMVG_main_IncrementalSfM'),  '-i', os.path.join(matchesDirectory, 'sfm_data.json'), '-m', matchesDirectory, '-o', reconstructionDirectory] + incrementalSFMOptions
            })

        if args.colorize:
            commands.append({
                'title': 'Colorize sparse point cloud', 
                'command': [os.path.join(openmvgBin, 'openMVG_main_ComputeSfM_DataColor'), '-i', os.path.join(reconstructionDirectory, 'sfm_data.bin'), '-o', os.path.join(reconstructionDirectory, 'colorized.ply') ]
            })

    if args.run_openmvs:
        sceneFileName = ['scene']

        commands.append({
            'title': 'Convert OpenMVG project to OpenMVS',
            'command': [os.path.join(openmvgBin, 'openMVG_main_openMVG2openMVS'), '-i', os.path.join(reconstructionDirectory, 'sfm_data.bin'), '-o', os.path.join(MVSDirectory, 'scene.mvs'), '-d', MVSDirectory]
        })

        # Do densifyPointCloud or not
        if args.densify or args.densify_only:
            commands.append({
                'title': 'Densify point cloud',
                'command': [os.path.join(openmvsBin, 'DensifyPointCloud'), 'scene.mvs', '-v', '0'] + densifyPointCloudOptions
            })
            sceneFileName.append('dense')

        if not args.densify_only:
            mvsFileName = '_'.join(sceneFileName) + '.mvs'
            commands.append({
                'title': 'Reconstruct mesh',
                'command': [os.path.join(openmvsBin, 'ReconstructMesh'), mvsFileName, '-v', '0'] + reconstructMeshOptions
            })
            sceneFileName.append('mesh')

            mvsFileName = '_'.join(sceneFileName) + '.mvs'
            rmCudaOk = False
            if args.rmcuda:
                if os.path.exists(os.path.join(openmvsBin, 'RefineMeshCUDA')):
                    rmCudaOk = True
            if rmCudaOk:
                commands.append({
                    'title': 'Refine mesh using CUDA',
                    'command': [os.path.join(openmvsBin, 'RefineMeshCUDA'), mvsFileName, '-v', '0'] + refineMeshOptions
                })
            else:
                commands.append({
                    'title': 'Refine mesh',
                    'command': [os.path.join(openmvsBin, 'RefineMesh'), mvsFileName, '-v', '0'] + refineMeshOptions
                })
            sceneFileName.append('refine')

            mvsFileName = '_'.join(sceneFileName) + '.mvs'
            commands.append({
                'title': 'Texture mesh',
                'command': [os.path.join(openmvsBin, 'TextureMesh'), mvsFileName, '-v', '0'] + textureMeshOptions
            })

    if args.debug:
        for instruction in commands:
            print(instruction['title'])
            print('=========================================================================')
            print(' '.join(map(str, instruction['command'])))
            print('')
        sys.exit()
    else:
        if args.run_openmvg and not os.path.exists(matchesDirectory):
            os.makedirs(matchesDirectory)
        if args.run_openmvg and not os.path.exists(reconstructionDirectory):
            os.makedirs(reconstructionDirectory)
        if args.run_openmvs and not os.path.exists(MVSDirectory):
            os.makedirs(MVSDirectory)

    return commands

def runCommand(cmd):
    cwd = outputDirectory
    if "OpenMVS" in cmd[0]:
        cwd = MVSDirectory
    try:
        p = subprocess.Popen(cmd, cwd = cwd)
        p.communicate()
        return p.returncode
    except OSError as err:
        if err.errno == errno.ENOENT:
            print("Could not find executable: {0} - Have you installed all the requirements?".format(cmd[0]))
        else:
            print("Could not run command: {0}".format(err))
        return -1
    except:
        print("Could not run command")
        return -1

def runCommands(commands):
    startTime = int(time.time())
    for instruction in commands:
        print(instruction['title'])
        print('=========================================================================')
        print(' '.join(map(str, instruction['command'])))
        print('')
        rc = runCommand(map(str, instruction['command']))
        if rc != 0:
            print('Failed while executing: ' )
            print(' '.join(map(str, instruction['command'])))
            sys.exit(1)
    endTime = int(time.time())

    timeDifference = endTime - startTime
    hours = int(math.floor(timeDifference / 60 / 60))
    minutes = int(math.floor((timeDifference - hours * 60 * 60) / 60))
    seconds = int(math.floor(timeDifference - (hours * 60 * 60 + minutes * 60)))
    print('\n\nFinished without errors (I guess) - Used time: {0}:{1}:{2}'.format(
        ('00' + str(hours))[-2:], 
        ('00' + str(minutes))[-2:], 
        ('00' + str(seconds))[-2:]))

parser = createParser()
args = parser.parse_args()
commands = createCommands(args)
runCommands(commands)
