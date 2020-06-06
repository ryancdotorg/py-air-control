import os
import json
import pprint


def test_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "testing/data.json"), "r") as json_file:
        with open(
            os.path.join(dir_path, "{}.md".format("Examples")), mode="w"
        ) as md_file:
            data = json.load(json_file)
            for client_type in data:
                create_header(md_file, client_type)
                create_data(md_file, data[client_type])
                md_file.write("---\n\n")


def create_header(md_file, client_type):
    md_file.write("# {}\n".format(client_type))


def create_data(md_file, client_data):
    for single_set in client_data:
        create_single_set(md_file, client_data[single_set])


def create_single_set(md_file, single_set):
    md_file.write(
        "## {} (Device: {})\n".format(single_set["info"], single_set["device"])
    )
    md_file.write("Execution:\n")
    for execute in single_set["execute"]:
        md_file.write("- {}\n".format(execute))

    md_file.write("\nOutput:\n\n")
    md_file.write("{}\n".format(replace_line_breaks(single_set["data"])))


def replace_line_breaks(current_string):
    return current_string.replace("\n", "<br/>\n")


test_data()