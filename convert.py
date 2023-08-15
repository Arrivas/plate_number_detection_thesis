import torch
import os

# Step 1: Export PyTorch model to ONNX format
model = torch.load('D:\\Codes\\python_\\thesis\\best.pt')
dummy_input = torch.randn(1, 3, 416, 416)
output_path = 'D:\\Codes\\python_\\thesis'
torch.onnx.export(model, dummy_input, output_path, opset_version=11)

# Step 2: Convert ONNX model to TensorFlow format
cmd = f'onnx-tf convert -i {output_path} -o {output_path[:-5]}_tf.pb'
os.system(cmd)

# Step 3: Convert TensorFlow model to TensorFlow.js format
cmd = f'tensorflowjs_converter --input_format=tf_saved_model --output_format=tfjs_graph_model --signature_name=serving_default --saved_model_tags=serve {output_path[:-5]}_tf.pb path/to/tfjs_model'
os.system(cmd)
