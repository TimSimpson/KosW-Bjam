import os
import paths
import subprocess
import sys

def get_ar_path():
    """Path to ar.exe."""
    if not os.path.exists(paths.AR):
        raise IOError("File not found:%s" % cmd)
    return paths.AR


def get_sh_elf_gpp_path():
    if not os.path.exists(paths.GPP):
        raise IOError("File not found:%s" % cmd)
    return paths.GPP


def create_dummy_file(file_path):
    with open(file_path, 'w') as file:
        file.write("This is a fake file created to appease Boost Build.")


class BjamCmd(object):

    def __init__(self, args):
        self.original_args = args

    def get_object_files(self):
        return [arg for arg in self.original_args if arg.endswith(".o")]

    def is_shared_lib_cmd(self):
        """If True, Boost Build is attempting to build a shared library."""
        for arg in self.original_args:
            if "--out-implib" in arg:
                return True
        return False

    def get_dll_file(self):
        """Finds and returns the dll Boost Build wants to create."""
        for arg in self.original_args:
            if arg.endswith(".dll"):  # Find the file we want.
                return arg
        raise Exception("Couldn't find the dll file!")

    def get_dll_a_file(self):
        """Finds and returns the shared lib Boost Build wants to create.

        This is buried in an argument on a call to the compiler which passes
        additional linker args.

        """
        def stripped_dlla_arg(argument):
            """This has linker args in it (looks like "-Wl,arg1,arg2,arg3")."""
            options = argument.split(",")
            for op in options:
                if op.endswith(".dll.a"):
                    return op
            raise Exception("Didn't find .dll.a in options.")

        for arg in self.original_args:
            if arg.endswith(".dll.a"):
                return stripped_dlla_arg(arg)
        raise Exception("Couldn't find the dll.a file!")


class GccRunner(object):

    def __init__(self, cmd):
        self.cmd = cmd

    def run(self):
        args = None
        if self.cmd.is_shared_lib_cmd():
            args = self.shared_lib_cmd()
        else:
            args = self.typical_cmd()
        exit_code = subprocess.call(args)
        if 0 != exit_code:
            exit(exit_code)
        if self.cmd.is_shared_lib_cmd():
            print("Writing fake file to trick Boost Build.")
            create_dummy_file(self.cmd.get_dll_file())

    def shared_lib_cmd(self):
        """Creates an arg list that correctly builds a Dreamcast shared lib."""
        new_args = [ get_ar_path(), "rcs", self.cmd.get_dll_a_file() ]
        new_args += self.cmd.get_object_files()
        return new_args

    def typical_cmd(self):
        return [ get_sh_elf_gpp_path() ] + self.cmd.original_args[1:]


if __name__=="__main__":
    cmd = BjamCmd(sys.argv)
    runner = GccRunner(cmd)
    runner.run()
