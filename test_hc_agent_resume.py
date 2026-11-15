import importlib.machinery
import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).parent / "bin" / "hc-agent-resume"
loader = importlib.machinery.SourceFileLoader("agent_resume", str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
agent_resume = importlib.util.module_from_spec(spec)
loader.exec_module(agent_resume)


class AgentResumeTest(unittest.TestCase):
    def test_record_round_trips(self):
        record = {"version": 1, "agent": "pi", "session": "abc-123", "cwd": "/tmp", "shellPid": 10}
        self.assertEqual(agent_resume.decode(agent_resume.encode(record)), record)

    def test_recovery_requires_a_replaced_shell(self):
        record = {"version": 1, "agent": "pi", "session": "abc-123", "cwd": "/tmp", "shellPid": 10}
        terminal = {"state": "live", "pid": 20, "foreground": {"argv": ["/bin/bash"]}}
        self.assertTrue(agent_resume.should_resume(terminal, record))
        self.assertFalse(agent_resume.should_resume({**terminal, "pid": 10}, record))
        self.assertFalse(agent_resume.should_resume({**terminal, "foreground": {"argv": ["vim"]}}, record))

    def test_resume_line_is_quoted_and_fixed(self):
        record = {"agent": "pi", "session": "abc-123", "cwd": "/tmp/it's here"}
        self.assertIsNone(agent_resume.resume_line(record))  # folder must exist
        record["cwd"] = "/tmp"
        self.assertEqual(agent_resume.resume_line(record), "cd -- /tmp && pi --session abc-123")


if __name__ == "__main__":
    unittest.main()
