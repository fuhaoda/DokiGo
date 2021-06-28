import os
import argparse

def split_sgfs(input_file_name, output_dir):
  if not os.path.isfile(input_file_name):
    raise Exception(f"There is no file with name {input_file_name}!")
  elif input_file_name.lower().split(".")[-1] != "sgfs":
    raise Exception(f"The input file with name {input_file_name} is not an sgfs file!")

  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Create a new directory with name {output_dir}.")

  with open(input_file_name,"rb") as f:
    sgfs_strings = f.readlines()

  idx = 0
  for sgf in sgfs_strings:
    while True:
      output_file_name = os.path.join(output_dir,'{:04d}'.format(idx)+'.sgf')
      idx += 1
      if not os.path.isfile(output_file_name):
        break
    with open(output_file_name, 'wb') as f:
      f.write(sgf)

if __name__ == "__main__":
  description = """
  Handle SGF/SGFS files
  """

  parser = argparse.ArgumentParser(description=description)
  parser.add_argument(
    "subcommand",
    help="Sub commands examples: split_sgfs"
  )
  parser.add_argument(
    "-input-file-name",
    help="Input sgfs file name",
    required=True
  )
  parser.add_argument(
    "-output-dir",
    help = "Ouptut sgf files location",
    required=True
  )
  args = vars(parser.parse_args())
  print(args)

  if(args["subcommand"] == "split_sgfs"):
    split_sgfs(args["input_file_name"], args["output_dir"])

