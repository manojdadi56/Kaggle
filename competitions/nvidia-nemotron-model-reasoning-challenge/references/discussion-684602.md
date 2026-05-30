# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684602
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 7392

---

Datasets
Models
Code
format_list_bulleted
Discussions
Learn
Kaggle Rankings
Progression
Documentation
Blog
Host a Competition
Research Grants
Educator Resources
Support/Contact
Community Guidelines
Team
Terms
Privacy
note_alt
NVIDIA Nemotron Model Reasoning Challenge
Is RLVR worth it? or should I work on SFT only?
Can We Train Externally and Upload submission.zip?
mamba_ssm facing error
PermissionDenied Error: ptxas-blackwell when training starts
Edited
Save order db V1
Kitesdata
History inferencing V3
History inferencing
Fork of inferencing
ARC Prize 2024
LMSYS - Chatbot Arena Human Preference Predictions
notebookc7a610ad46
train Swin_T[pytorch lightning]
Viral Pneumonia Classification | GoogLeNet
1
search
Kaggle uses cookies from Google to deliver and enhance the quality of its services and to analyze traffic.
NVIDIA · FEATURED PREDICTION COMPETITION · 17 DAYS TO GO
Submit Prediction
more_horiz
NVIDIA Nemotron Model Reasoning Challenge
Advance reasoning techniques using NVIDIA Nemotron open models on a novel benchmark
Overview
Data
Code
Models
Discussion
Leaderboard
Rules
Team
Submissions
TWEAK · 2275TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
3
arrow_drop_down
more_vert
Kaggle Environment Fixes for Nemotron-3-Nano (March 2026
Kaggle workaround for Nemotron-3-Nano (cutlass / quack, ptxas-blackwell, RMSNorm, fast path)
This is a workaround, not an ideal fix.
It forces the slow path, but it let us get model loading/training working on Kaggle.
The main issues I ran into were:
Missing cutlass and quack imports
ptxas-blackwell permission/path issues
Triton rmsnorm kernel crashes
Broken Nemotron fast-path CUDA kernels
Put this at the very top of your notebook, before your normal imports:
import os
import sys
import stat
import shutil
import types
import importlib.machinery
class _Dummy:
def __init__(self, *args, **kwargs):    pass
def __call__(self, *args, **kwargs):    return self
def __getattr__(self, name):            return self
def __iter__(self):                     return iter(())
def __bool__(self):                     return False
def __repr__(self):                     return "Dummy()"
def __or__(self, other):        return self
def __ror__(self, other):       return self
def __and__(self, other):       return self
def __rand__(self, other):      return self
def __xor__(self, other):       return self
def __rxor__(self, other):      return self
def __add__(self, other):       return self
def __radd__(self, other):      return self
def __sub__(self, other):       return self
def __rsub__(self, other):      return self
def __mul__(self, other):       return self
def __rmul__(self, other):      return self
def __floordiv__(self, other):  return self
def __truediv__(self, other):   return self
def __mod__(self, other):       return self
def __pow__(self, other):       return self
def __lshift__(self, other):    return self
def __rshift__(self, other):    return self
def __lt__(self, other):        return False
def __le__(self, other):        return False
def __gt__(self, other):        return False
def __ge__(self, other):        return False
def __eq__(self, other):        return False
def __ne__(self, other):        return True
def __hash__(self):             return 0
def __int__(self):              return 0
def __float__(self):            return 0.0
def __index__(self):            return 0
def __len__(self):              return 0
def __contains__(self, x):      return False
def __getitem__(self, key):     return self
def __setitem__(self, k, v):    pass
def __class_getitem__(cls, item): return _Dummy()
class _FakeModule(types.ModuleType):
def __getattr__(self, name):
return _Dummy()
def _fake_pkg(name: str):
mod = _FakeModule(name)
mod.__file__ = f"/tmp/{name.replace('.', '/')}.py"
mod.__package__ = name.rpartition(".")[0] if "." in name else name
mod.__path__ = [f"/tmp/{name.replace('.', '/')}"]
mod.__loader__ = None
mod.__spec__ = importlib.machinery.ModuleSpec(
name=name, loader=None, origin=mod.__file__, is_package=True,
)
return mod
def _fake_mod(name: str):
mod = _FakeModule(name)
mod.__file__ = f"/tmp/{name.replace('.', '/')}.py"
mod.__package__ = name.rpartition(".")[0]
mod.__loader__ = None
mod.__spec__ = importlib.machinery.ModuleSpec(
name=name, loader=None, origin=mod.__file__, is_package=False,
)
return mod
_quack = _fake_pkg("quack")
sys.modules["quack"] = _quack
_compile_utils = _fake_mod("quack.compile_utils")
_compile_utils.make_fake_tensor = lambda *args, **kwargs: _Dummy()
sys.modules["quack.compile_utils"] = _compile_utils
_cute_dsl_utils = _fake_mod("quack.cute_dsl_utils")
_cute_dsl_utils.torch2cute_dtype_map = {}
sys.modules["quack.cute_dsl_utils"] = _cute_dsl_utils
for _sub in ["quack.fast", "quack.modeling", "quack.ops", "quack.utils"]:
sys.modules[_sub] = _fake_pkg(_sub)
_cutlass = _fake_pkg("cutlass")
_cutlass.const_expr = lambda x: x
_cute = _fake_pkg("cutlass.cute")
_cutlass.cute = _cute
sys.modules["cutlass"] = _cutlass
sys.modules["cutlass.cute"] = _cute
print("[fix] Stubbed quack + cutlass")
_ptxas_src = None
for _candidate in [
"/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell",
"/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/triton/backends/nvidia/bin/ptxas-blackwell",
]:
if os.path.exists(_candidate):
_ptxas_src = _candidate
break
_ptxas_dst = "/tmp/ptxas-blackwell"
if _ptxas_src and os.path.exists(_ptxas_src):
shutil.copy2(_ptxas_src, _ptxas_dst)
os.chmod(_ptxas_dst, os.stat(_ptxas_dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
import triton.backends.nvidia as nv_backend
_src_bin = os.path.join(os.path.dirname(nv_backend.__file__), "bin")
_dst_bin = "/tmp/triton_nvidia_bin"
shutil.copytree(_src_bin, _dst_bin, dirs_exist_ok=True)
for _f in os.listdir(_dst_bin):
_fp = os.path.join(_dst_bin, _f)
if os.path.isfile(_fp):
os.chmod(_fp, os.stat(_fp).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
nv_backend.__file__ = os.path.join(_dst_bin, "..", "__init__.py")
os.environ["TRITON_PTXAS_PATH"] = _ptxas_dst
os.environ["TRITON_PTXAS_BLACKWELL_PATH"] = _ptxas_dst
print(f"[fix] Copied ptxas-blackwell from {_ptxas_src}")
else:
print("[fix] ptxas-blackwell not found")
import torch
import torch.nn.functional as F
def _pure_rmsnorm_fn(x, weight, bias=None, z=None, eps=1e-5,
group_size=None, norm_before_gate=True, upcast=True):
dtype = x.dtype
if upcast:
x = x.float()
variance = x.pow(2).mean(-1, keepdim=True)
x_normed = x * torch.rsqrt(variance + eps)
out = x_normed * weight.float()
if bias is not None:
out = out + bias.float()
if z is not None:
out = out * F.silu(z.float())
return out.to(dtype)
for _name, _mod in list(sys.modules.items()):
if hasattr(_mod, "rmsnorm_fn"):
_mod.rmsnorm_fn = _pure_rmsnorm_fn
print("[fix] Patched rmsnorm to pure PyTorch")
print("[fix] All Kaggle environment fixes applied")
Then after from_pretrained() run:
for name, mod in sys.modules.items():
if "modeling_nemotron_h" in name:
mod.is_fast_path_available = False
print(f"[fix] Disabled fast path in {name}")
This is just a workaround, but it got us unstuck.
add_reaction
React
0 Comments
Hotness
undo
redo
format_size
format_bold
format_italic
format_strikethrough
insert_link
format_quote
format_list_numbered
format_list_bulleted
table_chart
insert_photo
smart_display
insert_emoticon
This comment will be made public once posted.
attach_file
Post Comment
