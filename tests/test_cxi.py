import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class CxiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cxi-test-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name).resolve()
        self.root = self.path/"instances"
        binary = self.path/"bin";binary.mkdir()
        fake = binary/"codex"
        fake.write_text('#!/usr/bin/env python3\nimport json,os,sys\nprint(json.dumps({"args":sys.argv[1:],"cwd":os.getcwd(),"home":os.environ.get("CODEX_HOME"),"key":os.environ.get("OPENAI_API_KEY")}))\n')
        fake.chmod(0o700)
        self.env = {**os.environ, "CXI_ROOT": str(self.root), "PATH": str(binary)+os.pathsep+os.environ["PATH"], "OPENAI_API_KEY": "fixture-parent-key"}

    def run_shell(self, command, shell="bash", ok=True):
        extension = "zsh" if shell == "zsh" else "bash"
        result = subprocess.run([shell, "-c", '. '+shlex.quote(str(SOURCE/("cxi."+extension)))+'; '+command],
            env=self.env, cwd=self.path, capture_output=True, text=True)
        if ok:self.assertEqual(result.returncode, 0, result.stderr)
        else:self.assertNotEqual(result.returncode, 0)
        return result

    def test_instances_keep_arguments_cwd_and_separate_home(self):
        for shell in ("bash", "zsh"):
            if not shutil.which(shell):continue
            with self.subTest(shell=shell):
                name="work-"+shell
                self.run_shell("cxi new "+name, shell)
                result=self.run_shell('cxi '+name+' "prompt with spaces" --model example', shell)
                data=json.loads(result.stdout)
                self.assertEqual(data["args"], ["prompt with spaces", "--model", "example"])
                self.assertEqual(Path(data["home"]), self.root/name)
                self.assertEqual(data["cwd"], str(self.path))
                self.assertIsNone(data["key"])

    def test_cloning_keeps_settings_but_not_login_or_sessions(self):
        self.run_shell("cxi new work")
        source=self.root/"work"
        (source/"config.toml").write_text('model="example"\n')
        (source/"auth.json").write_text('{"fixture":"private"}')
        (source/"sessions").mkdir()
        self.run_shell("cxi new personal --from work")
        target=self.root/"personal"
        self.assertEqual((target/"config.toml").read_bytes(),(source/"config.toml").read_bytes())
        self.assertFalse((target/"auth.json").exists())
        self.assertFalse((target/"sessions").exists())

    def test_invalid_names_and_symlinks_are_rejected(self):
        for name in ("../outside", "default", "help", ".hidden"):
            self.run_shell('cxi new '+shlex.quote(name),ok=False)
        self.root.mkdir(exist_ok=True)
        (self.root/"linked").symlink_to(self.path,target_is_directory=True)
        self.run_shell("cxi linked",ok=False)

    def test_instance_environment_is_scoped_to_that_launch(self):
        self.run_shell("cxi new work")
        (self.root/"work/cxi.env").write_text('export OPENAI_API_KEY="fixture-instance-key"\n')
        result=self.run_shell('cxi work; printf "parent=%s\\n" "$OPENAI_API_KEY"')
        lines=result.stdout.splitlines()
        self.assertEqual(json.loads(lines[0])["key"],"fixture-instance-key")
        self.assertEqual(lines[1],"parent=fixture-parent-key")

    def test_login_arguments_are_forwarded(self):
        self.run_shell("cxi new work")
        result=self.run_shell("cxi login work --device-auth")
        self.assertEqual(json.loads(result.stdout)["args"],["login","--device-auth"])

    def test_existing_home_alias_runs_without_moving_or_deleting_files(self):
        external=self.path/"external home";external.mkdir()
        (external/"config.toml").write_text('model="example"\n')
        for shell in ("bash", "zsh"):
            if not shutil.which(shell):continue
            name="outside-"+shell
            self.run_shell('cxi add '+name+' '+shlex.quote(str(external)),shell)
            result=self.run_shell('cxi '+name+' "external prompt"',shell)
            self.assertEqual(json.loads(result.stdout)["home"],str(external))
            self.assertIn(name,self.run_shell('cxi ls',shell).stdout)
            self.run_shell('cxi rm '+name+' -f',shell)
            self.assertTrue((external/"config.toml").exists())
            self.run_shell('cxi '+name,shell,ok=False)

    def test_offline_installer_is_repeatable(self):
        subprocess.run(["python3",str(SOURCE/"scripts/build_release.py")],check=True,capture_output=True)
        target=self.path/"install"
        args=["bash",str(SOURCE/"dist/install.sh"),"--from-dir",str(SOURCE/"dist"),"--prefix",str(target),"--no-rc","--shell","both"]
        for _ in range(2):
            result=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((target/"cxi.bash").exists())


if __name__ == "__main__":unittest.main()
