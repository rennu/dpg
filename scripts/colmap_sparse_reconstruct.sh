# Usage:
# 1. Make sure your images are in /your/projet/path/images folder
# 2. cd /your/project/path && colmap_sparse_reconstruct.sh
PROJECT_PATH=$(pwd)
COLMAPBIN=/opt/colmap/bin/colmap
# Replace with 1 if you you plan to use GPU
USE_GPU=0

/opt/colmap/bin/colmap feature_extractor \
  --database_path ${PROJECT_PATH}/database.db \
  --image_path ${PROJECT_PATH}/images \
  --SiftExtraction.max_image_size 10000 \
  --SiftExtraction.max_num_features 32768 \
  --SiftExtraction.use_gpu ${USE_GPU}

/opt/colmap/bin/colmap exhaustive_matcher \
  --database_path ${PROJECT_PATH}/database.db \
  --SiftMatching.use_gpu ${USE_GPU}

mkdir ${PROJECT_PATH}/sparse

/opt/colmap/bin/colmap mapper \
  --database_path ${PROJECT_PATH}/database.db \
  --image_path ${PROJECT_PATH}/images \
  --export_path ${PROJECT_PATH}/sparse

mkdir ${PROJECT_PATH}/dense

/opt/colmap/bin/colmap model_converter \
  --input_path ${PROJECT_PATH}/sparse/0 \
  --output_path ./sparse.nvm \
  --output_type NVM

