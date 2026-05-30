# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/681820
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 27256

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
symbol_transformation class problem can have multiple valid candidate answer
[update] Read CPMP's reply. [original] Do not distill models that do not allow distillation (e.g. gemini, gpt5)
[Fake Notebook Alert] Watch out for fake laptops that copy and upload other people's submission.
Are problem types the same for train and test?
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
ADARSH KUMAR · 762ND IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
23
arrow_drop_down
more_vert
Fix for “CUDA error: no kernel image is available for execution on the device” on RTX PRO 6000 Blackwell
This competition provides an NVIDIA RTX PRO 6000 Blackwell GPU. When trying to fine-tune the Nemotron model with LoRA, you may encounter the following error during training:
AcceleratorError: CUDA error: no kernel image is available for execution on the device
I initially thought something was wrong in my training pipeline and spent 2–3 hours debugging tokenization, Trainer setup, LoRA configuration, etc. However, the issue is actually much simpler.
Reason: The default PyTorch build in the environment supports CUDA architectures up to sm_90, but the RTX PRO 6000 (Blackwell) uses sm_120. Because of this mismatch, CUDA kernels cannot run and training fails.
Solution: Install a PyTorch build compiled with CUDA 12.8+ (nightly) that includes support for the Blackwell architecture.
Run this before importing torch or transformers:
!pip uninstall -y torch torchvision torchaudio
!pip install --no-cache-dir torch torchvision torchaudio --index-url
https://download.pytorch.org/whl/nightly/cu128
!pip install mamba-ssm --no-build-isolation
After installing, restart the kernel from the Run menu, and the training should start normally.
Hope this saves others some debugging time 🙂
3
add_reaction
16 Comments
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
Pinned comments
push_pin
Tiffany Xiang
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
4
arrow_drop_down
more_vert
The new Docker image with CUDA 12.8 and updated PyTorch is rolled out now! Thanks everyone for your patience :)
reply
Reply
add_reaction
React
mindset324
Posted 2 months ago
· 1634th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Still it is showing “CUDA error: no kernel image is available for execution on the device” on RTX PRO 6000 Blackwell . Could you please explain in detail how to fix this ?
reply
Reply
add_reaction
React
Dustin
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
@mindset324 Please share a minimal notebook which demonstrates the issue, thats the best way for us to be able to evaluate whats going on.
reply
Reply
add_reaction
React
kunal_wagh2703
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Still getting those same errors for the Docker Filer! And when you try to: !pip uninstall -y torch torchvision torchaudio It says read only file system ofc! I have a minimal and basic pipeline for now.
``--------------------------------------------------------------------------- AcceleratorError Traceback (most recent call last) /tmp/ipykernel_161/874017041.py in () ----> 1 train_result = trainer.train() 2 print(train_result)
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/transformers/trainer.py in train(self, resume_from_checkpoint, trial, ignore_keys_for_eval) 1422 ctx = suppress_progress_bars() if args.push_to_hub else contextlib.nullcontext() 1423 with ctx: -> 1424 return inner_training_loop( 1425 args=args, 1426 resume_from_checkpoint=resume_from_checkpoint,
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/transformers/trainer.py in _inner_training_loop(self, batch_size, args, resume_from_checkpoint, trial, ignore_keys_for_eval) 1504 for epoch in range(epochs_trained, num_train_epochs): 1505 self.control = self.callback_handler.on_epoch_begin(self.args, self.state, self.control) -> 1506 self._run_epoch( 1507 model=model, 1508 epoch=epoch,
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/transformers/trainer.py in _run_epoch(self, model, epoch, train_dataloader, steps_in_epoch, num_update_steps_per_epoch, trial, ignore_keys_for_eval, start_time, resume_from_checkpoint, epochs_trained, steps_trained_in_current_epoch) 1732 sync_context = functools.partial(self.accelerator.no_sync, model=model) 1733 with sync_context(): -> 1734 tr_loss_step = self.training_step(model, inputs, num_items_in_batch) 1735 1736 if (
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/transformers/trainer.py in training_step(self, model, inputs, num_items_in_batch) 1904 1905 with self.compute_loss_context_manager(): -> 1906 loss = self.compute_loss(model, inputs, num_items_in_batch=num_items_in_batch) 1907 1908 del inputs
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/transformers/trainer.py in compute_loss(self, model, inputs, return_outputs, num_items_in_batch) 1976 kwargs["num_items_in_batch"] = num_items_in_batch 1977 inputs = {**inputs, *kwargs} -> 1978 outputs = model(*inputs) 1979 1980 # User-defined compute_loss function
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _wrapped_call_impl(self, *args, *kwargs) 1776 return self._compiled_call_impl(args, *kwargs) # type: ignore[misc] 1777 else: -> 1778 return self._call_impl(args, **kwargs) 1779 1780 # torchrec tests the code consistency with the following code
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _call_impl(self, *args, *kwargs) 1787 or _global_backward_pre_hooks or _global_backward_hooks 1788 or _global_forward_hooks or _global_forward_pre_hooks): -> 1789 return forward_call(args, **kwargs) 1790 1791 result = None
/usr/local/lib/python3.12/dist-packages/accelerate/utils/operations.py in forward(*args, *kwargs) 817 818 def forward(args, *kwargs): --> 819 return model_forward(args, **kwargs) 820 821 # To act like a decorator so that it can be popped when doing extract_model_from_parallel
/usr/local/lib/python3.12/dist-packages/accelerate/utils/operations.py in call(self, *args, **kwargs) 805 806 def call(self, *args, *kwargs): --> 807 return convert_to_fp32(self.model_forward(args, **kwargs)) 808 809 def getstate(self):
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/amp/autocast_mode.py in decorate_autocast(*args, *kwargs) 42 def decorate_autocast(args, *kwargs): 43 with autocast_instance: ---> 44 return func(args, **kwargs) 45 46 decorate_autocast.__script_unsupported = ( # type: ignore[attr-defined]
/usr/local/lib/python3.12/dist-packages/accelerate/utils/operations.py in forward(*args, *kwargs) 817 818 def forward(args, *kwargs): --> 819 return model_forward(args, **kwargs) 820 821 # To act like a decorator so that it can be popped when doing extract_model_from_parallel
/usr/local/lib/python3.12/dist-packages/accelerate/utils/operations.py in call(self, *args, **kwargs) 805 806 def call(self, *args, *kwargs): --> 807 return convert_to_fp32(self.model_forward(args, **kwargs)) 808 809 def getstate(self):
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/amp/autocast_mode.py in decorate_autocast(*args, *kwargs) 42 def decorate_autocast(args, *kwargs): 43 with autocast_instance: ---> 44 return func(args, **kwargs) 45 46 decorate_autocast.__script_unsupported = ( # type: ignore[attr-defined]
/usr/local/lib/python3.12/dist-packages/peft/peft_model.py in forward(self, input_ids, attention_mask, inputs_embeds, labels, output_attentions, output_hidden_states, return_dict, task_ids, kwargs) 1921 with self._enable_peft_forward_hooks(kwargs): 1922 kwargs = {k: v for k, v in kwargs.items() if k not in self.special_peft_forward_args} -> 1923 return self.base_model( 1924 input_ids=input_ids, 1925 attention_mask=attention_mask,
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _wrapped_call_impl(self, *args, *kwargs) 1776 return self._compiled_call_impl(args, *kwargs) # type: ignore[misc] 1777 else: -> 1778 return self._call_impl(args, **kwargs) 1779 1780 # torchrec tests the code consistency with the following code
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _call_impl(self, *args, *kwargs) 1787 or _global_backward_pre_hooks or _global_backward_hooks 1788 or _global_forward_hooks or _global_forward_pre_hooks): -> 1789 return forward_call(args, **kwargs) 1790 1791 result = None
/usr/local/lib/python3.12/dist-packages/peft/tuners/tuners_utils.py in forward(self, *args, **kwargs) 309 310 def forward(self, *args: Any, *kwargs: Any): --> 311 return self.model.forward(args, **kwargs) 312 313 def _pre_injection_hook(self, model: nn.Module, config: PeftConfig, adapter_name: str) -> None:
~/.cache/huggingface/modules/transformers_modules/_1/modeling_nemotron_h.py in forward(self, input_ids, inputs_embeds, position_ids, cache_params, labels, output_attentions, output_hidden_states, return_dict, use_cache, cache_position, attention_mask, **kwargs) 1700 return_dict = return_dict if return_dict is not None else self.config.use_return_dict 1701 -> 1702 nemotron_h_outputs = self.backbone( 1703 input_ids, 1704 cache_params=cache_params,
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _wrapped_call_impl(self, *args, *kwargs) 1776 return self._compiled_call_impl(args, *kwargs) # type: ignore[misc] 1777 else: -> 1778 return self._call_impl(args, **kwargs) 1779 1780 # torchrec tests the code consistency with the following code
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _call_impl(self, *args, *kwargs) 1787 or _global_backward_pre_hooks or _global_backward_hooks 1788 or _global_forward_hooks or _global_forward_pre_hooks): -> 1789 return forward_call(args, **kwargs) 1790 1791 result = None
~/.cache/huggingface/modules/transformers_modules/_1/modeling_nemotron_h.py in forward(self, input_ids, inputs_embeds, position_ids, cache_params, use_cache, output_attentions, output_hidden_states, return_dict, cache_position, attention_mask, **kwargs) 1491 ) 1492 else: -> 1493 hidden_states = mixer_block( 1494 hidden_states, 1495 cache_params=cache_params,
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _wrapped_call_impl(self, *args, *kwargs) 1776 return self._compiled_call_impl(args, *kwargs) # type: ignore[misc] 1777 else: -> 1778 return self._call_impl(args, **kwargs) 1779 1780 # torchrec tests the code consistency with the following code
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _call_impl(self, *args, *kwargs) 1787 or _global_backward_pre_hooks or _global_backward_hooks 1788 or _global_forward_hooks or _global_forward_pre_hooks): -> 1789 return forward_call(args, **kwargs) 1790 1791 result = None
~/.cache/huggingface/modules/transformers_modules/_1/modeling_nemotron_h.py in forward(self, hidden_states, cache_params, cache_position, attention_mask) 775 776 if self.block_type == "mamba": --> 777 hidden_states = self.mixer( 778 hidden_states, cache_params=cache_params, cache_position=cache_position 779 )
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _wrapped_call_impl(self, *args, *kwargs) 1776 return self._compiled_call_impl(args, *kwargs) # type: ignore[misc] 1777 else: -> 1778 return self._call_impl(args, **kwargs) 1779 1780 # torchrec tests the code consistency with the following code
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/nn/modules/module.py in _call_impl(self, *args, *kwargs) 1787 or _global_backward_pre_hooks or _global_backward_hooks 1788 or _global_forward_hooks or _global_forward_pre_hooks): -> 1789 return forward_call(args, **kwargs) 1790 1791 result = None
~/.cache/huggingface/modules/transformers_modules/_1/modeling_nemotron_h.py in forward(self, hidden_states, cache_params, cache_position, attention_mask) 713 ): 714 if is_fast_path_available and "cuda" in self.in_proj.weight.device.type: --> 715 return self.cuda_kernels_forward(hidden_states, cache_params, cache_position, attention_mask) 716 dtype = hidden_states.dtype 717 if attention_mask is not None and attention_mask.shape[1] > 1 and attention_mask.shape[0] > 1:
~/.cache/huggingface/modules/transformers_modules/_1/modeling_nemotron_h.py in cuda_kernels_forward(self, hidden_states, cache_params, cache_position, attention_mask) 427 # 2-4. Fused kernel for conv1d, SSM, and the final projection 428 if self.training and cache_params is None: --> 429 out = mamba_split_conv1d_scan_combined( 430 projected_states, 431 self.conv1d.weight.squeeze(1),
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/mamba_ssm/ops/triton/ssd_combined.py in mamba_split_conv1d_scan_combined(zxbcdt, conv1d_weight, conv1d_bias, dt_bias, A, D, chunk_size, initial_states, seq_idx, dt_limit, return_final_states, activation, rmsnorm_weight, rmsnorm_eps, outproj_weight, outproj_bias, headdim, ngroups, norm_before_gate) 995 out: (batch, seqlen, dim) 996 """ --> 997 return MambaSplitConv1dScanCombinedFn.apply(zxbcdt, conv1d_weight, conv1d_bias, dt_bias, A, D, chunk_size, initial_states, seq_idx, dt_limit, return_final_states, activation, rmsnorm_weight, rmsnorm_eps, outproj_weight, outproj_bias, headdim, ngroups, norm_before_gate) 998 999
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/autograd/function.py in apply(cls, *args, *kwargs) 594 # See NOTE: [functorch vjp and autograd interaction] 595 args = _functorch.utils.unwrap_dead_wrappers(args) --> 596 return super().apply(args, **kwargs) # type: ignore[misc] 597 598 if not is_setup_ctx_defined:
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/amp/autocast_mode.py in decorate_fwd(*args, *kwargs) 486 if cast_inputs is None: 487 args[0]._fwd_used_autocast = torch.is_autocast_enabled(device_type) --> 488 return fwd(args, **kwargs) # pyrefly: ignore [not-callable] 489 else: 490 autocast_context = torch.is_autocast_enabled(device_type)
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/mamba_ssm/ops/triton/ssd_combined.py in forward(ctx, zxbcdt, conv1d_weight, conv1d_bias, dt_bias, A, D, chunk_size, initial_states, seq_idx, dt_limit, return_final_states, activation, rmsnorm_weight, rmsnorm_eps, outproj_weight, outproj_bias, headdim, ngroups, norm_before_gate) 839 seq_idx = seq_idx.contiguous() if seq_idx is not None else None 840 xBC_conv = rearrange( --> 841 causal_conv1d_fwd_function(rearrange(ensure_stride(xBC), "b s d -> b d s"), 842 conv1d_weight, conv1d_bias, seq_idx, None, None, activation in ["silu", "swish"]), 843 "b d s -> b s d"
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/causal_conv1d/cpp_functions.py in causal_conv1d_fwd_function(x, weight, bias, seq_idx, initial_states, final_states_out, silu_activation) 102 ) -> torch.Tensor: 103 out = torch.empty_like(x) --> 104 _causal_conv1d_fwd_cpp( 105 x=x, 106 weight=weight,
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_library/custom_ops.py in call(self, *args, **kwargs) 724 725 def call(self, *args, *kwargs): --> 726 return self._opoverload(args, **kwargs) 727 728 def register_vmap(
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_ops.py in call(self, *args, **kwargs) 869 # that are named "self". This way, all the aten ops can be called by kwargs. 870 def call(self, /, *args: _P.args, *kwargs: _P.kwargs) -> _T: --> 871 return self._op(args, **kwargs) 872 873 # Use positional-only argument to avoid naming collision with aten ops arguments
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_library/autograd.py in autograd_impl(keyset, *args, *keyword_only_args) 110 result = Generated.apply(args, Metadata(keyset, keyword_only_args)) # type: ignore[attr-defined] 111 else: --> 112 result = forward_no_grad(*args, Metadata(keyset, keyword_only_args)) 113 return result 114
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_library/autograd.py in forward_no_grad(*args) 39 keyset = metadata.keyset 40 kwargs = metadata.keyword_only_args ---> 41 result = op.redispatch(keyset & _C._after_autograd_keyset, *args, **kwargs) 42 return result 43
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_ops.py in redispatch(self, keyset, *args, **kwargs) 876 self, /, keyset: torch._C.DispatchKeySet, *args: _P.args, **kwargs: _P.kwargs 877 ) -> _T: --> 878 return self._handle.redispatch_boxed(keyset, *args, **kwargs) # type: ignore[return-value] 879 880 def hash(self):
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_library/custom_ops.py in adinplaceorview_impl(keyset, *args, **kwargs) 688 increment_version(kwargs[key]) 689 # Handle view + mutation that are in the schema --> 690 return original_kernel.call_boxed(keyset, *args, **kwargs) 691 692 with warnings.catch_warnings():
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_library/custom_ops.py in backend_impl(*args, *kwargs) 373 374 def backend_impl(args, *kwargs): --> 375 result = self._backend_fns[device_type](args, **kwargs) 376 377 def get_module():
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_compile.py in inner(*args, *kwargs) 52 fn.__dynamo_disable = disable_fn # type: ignore[attr-defined] 53 ---> 54 return disable_fn(args, **kwargs) 55 56 return inner
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_dynamo/eval_frame.py in _fn(*args, *kwargs) 1270 ): 1271 return fn(args, *kwargs) -> 1272 return fn(args, **kwargs) 1273 finally: 1274 set_eval_frame(None)
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torch/_library/custom_ops.py in wrapped_fn(*args, *kwargs) 408 return self._init_fn(args, *kwargs) 409 else: --> 410 return fn(args, **kwargs) 411 412 self._backend_fns[device_type] = wrapped_fn
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/causal_conv1d/cpp_functions.py in _causal_conv1d_fwd_cpp(x, weight, bias, seq_idx, initial_states, out, final_states_out, silu_activation) 20 silu_activation: bool, 21 ) -> None: ---> 22 causal_conv1d_cuda.causal_conv1d_fwd( 23 x, 24 weight,
AcceleratorError: CUDA error: no kernel image is available for execution on the device Search for cudaErrorNoKernelImageForDevice' in https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__TYPES.html for more information. CUDA kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect. For debugging consider passing CUDA_LAUNCH_BLOCKING=1 Compile withTORCH_USE_CUDA_DSA` to enable device-side assertions.
reply
Reply
add_reaction
React
mindset324
Posted 2 months ago
· 1634th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
2026-03-24 18:58:00,171 - INFO - Initializing device manager… 2026-03-24 18:58:16,456 - INFO - GPU detected: NVIDIA RTX PRO 6000 Blackwell Server Edition 2026-03-24 18:58:16,457 - INFO - CUDA version: 12.8 2026-03-24 18:58:16,457 - INFO - Compute capability: 12.0 2026-03-24 18:58:16,457 - INFO - GPU memory: 94.97 GB 2026-03-24 18:58:16,458 - INFO - Detecting available attention mechanisms… 2026-03-24 18:58:16,511 - INFO - Flash Attention 2: Available 2026-03-24 18:58:16,512 - INFO - SDPA (PyTorch): Available 2026-03-24 18:58:26,119 - INFO - Mamba SSM: Not available (No module named 'cutlass')
reply
Reply
add_reaction
React
Evgeniy Glukhov
Posted 2 months ago
· 3627th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Thank you for the update! Now I got ModuleNotFoundError: No module named 'cutlass' Should I recreate the notebook somehow?
reply
Reply
add_reaction
React
kunal_wagh2703
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Same here, have you got any solution to this??
reply
Reply
add_reaction
React
Adarsh Kumar
TOPIC AUTHOR
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
!pip install nvidia-cutlass-dsl
Just do it, it will work then
reply
Reply
add_reaction
React
All other comments
Dustin
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
5
arrow_drop_down
more_vert
@tifftoff Can you look into upgrading these in the base env for the next release? May need to check in with our base image since I think they are installed there.
reply
Reply
4
2
add_reaction
xianxu qiu
Posted 2 months ago
· 2574th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
The inference speed is too slow, only 1.7 tokens/s. It seems the CUDA version is incompatible. Can the official mirror be updated?
reply
Reply
add_reaction
React
HanJunseo
Posted 2 months ago
· 2312th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
me too. I can't solve this problem
reply
Reply
add_reaction
React
Anton Kratz
Posted 2 months ago
· 3141st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks for speaking up. I have spent ~5 of the weekly GPU hours on this already plus additional troubleshooting. This is a blocker.
reply
Reply
add_reaction
React
Anton Kratz
Posted 2 months ago
· 3141st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Thank you @adarsh2626 for posting this. I am indeed running into this exact error, however the solution does not work for me, when I try your solution I get:
Found existing installation: torch 2.12.0.dev20260315+cu128
Uninstalling torch-2.12.0.dev20260315+cu128:
ERROR: Exception:
Traceback (most recent call last):
File "/usr/lib/python3.12/shutil.py", line 847, in move
os.rename(src, real_dst)
OSError: [Errno 18] Invalid cross-device link: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/bin/torchfrtrace' -> '/tmp/pip-uninstall-jrvck2ey/torchfrtrace'
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
File "/usr/local/lib/python3.12/dist-packages/pip/_internal/cli/base_command.py", line 179, in exc_logging_wrapper
status = run_func(*args)
^^^^^^^^^^^^^^^
File "/usr/local/lib/python3.12/dist-packages/pip/_internal/commands/uninstall.py", line 106, in run
uninstall_pathset = req.uninstall(
^^^^^^^^^^^^^^
File "/usr/local/lib/python3.12/dist-packages/pip/_internal/req/req_install.py", line 722, in uninstall
uninstalled_pathset.remove(auto_confirm, verbose)
File "/usr/local/lib/python3.12/dist-packages/pip/_internal/req/req_uninstall.py", line 370, in remove
moved.stash(path)
File "/usr/local/lib/python3.12/dist-packages/pip/_internal/req/req_uninstall.py", line 261, in stash
renames(path, new_path)
File "/usr/local/lib/python3.12/dist-packages/pip/_internal/utils/misc.py", line 356, in renames
shutil.move(old, new)
File "/usr/lib/python3.12/shutil.py", line 868, in move
os.unlink(src)
OSError: [Errno 30] Read-only file system: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/bin/torchfrtrace'
reply
Reply
add_reaction
React
This comment has been deleted.
Adarsh Kumar
TOPIC AUTHOR
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
@antonkratz can you try
!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
OR
!pip install torch torchvision torchaudio \
--index-url https://download.pytorch.org/whl/cu128 \
--force-reinstall --no-deps
The problem is the pytorch version it should be 128
And you need this to load model
!pip install mamba-ssm --no-build-isolation
If you get retrying or internetconnection error turn off and again on the notebooks internet it will work
reply
Reply
add_reaction
React
Anton Kratz
Posted 2 months ago
· 3141st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thank you, but somehow I can't seem to get it to work. I tried the these two fixes just now.
It seems I do have 128 installed already?!
I took the freedom to share my notebook with you, I hope that's okay. Maybe I could kindly ask you to take a look?
P.S.:
!pip install torch torchvision torchaudio \
--index-url https://download.pytorch.org/whl/cu128 \
--force-reinstall --no-deps
results in ERROR: Could not install packages due to an OSError: [Errno 30] Read-only file system: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/torchaudio-2.11.0.dev20260315+cu128.dist-info/'
What does work for me is
!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
however it will ultimately result in AcceleratorError: CUDA error: no kernel image is available for execution on the device.
reply
Reply
add_reaction
React
6 more replies
arrow_drop_down
HanJunseo
Posted 2 months ago
· 2312th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
I tried again today, and it seems that internet access is blocked in the competition notebook environment. Is this happening only to me, or are others seeing the same issue as well?
reply
Reply
add_reaction
React
Keanan
Posted 2 months ago
· 2008th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
got this message: Error: Internet cannot be enabled for this competition with the current accelerator.
reply
Reply
add_reaction
React
YellwoJune083
Posted 2 months ago
· 3643rd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I fixed this by copying and editing 'demo code' in link: https://www.kaggle.com/code/ryanholbrook/nvidia-nemotron-submission-demo
I copied this and turned internet on, and changed accelerator to blackwell, it worked.
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down
Anton Kratz
Posted 2 months ago
· 3141st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Exactly the same happened to me today, too.
reply
Reply
add_reaction
React
HADY
Posted 2 months ago
· 3530th in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
How did you access the rtx pro 6000?
reply
Reply
add_reaction
React
lucian kucera
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Ver simple in code tab u create notebook, which is asociated with this competition and u can use rtx pro 6000.
reply
Reply
add_reaction
React
Keanan
Posted 2 months ago
· 2008th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
here is my fix
reply
Reply
add_reaction
React
