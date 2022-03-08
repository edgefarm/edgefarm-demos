from edgefarm_application.base.schema import schema_load_builtin, schema_read_builtin
import os


def schema_read(code_rel_path, schema_name):
    return schema_read_builtin(
        code_rel_path, os.path.join(schema_path(), f"{schema_name}.avsc")
    )


def schema_load(code_rel_path, schema_name):
    return schema_load_builtin(code_rel_path, os.path.join(schema_path(), schema_name))


def schema_path():
    return os.getenv("SCHEMA_PATH", os.path.join("..", "..", "schemas"))
