"""
Training Loop Implementation
"""

import torch
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
from tqdm.auto import tqdm
import time
from datetime import datetime

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

from ..config import config, CHECKPOINTS_DIR, FINAL_MODELS_DIR, OUTPUTS_DIR
from ..utils import save_json, format_time, print_model_info
from .metrics import VQAMetrics, compute_batch_accuracy


class VQATrainer:
    """VQA Model Trainer"""

    def __init__(
        self,
        model,
        train_loader,
        val_loader,
        device,
        answer_to_label,
        label_to_answer,
        use_wandb=True,
    ):
        """
        Initialize trainer

        Args:
            model: VQA model
            train_loader: Training dataloader
            val_loader: Validation dataloader
            device: Device to train on
            answer_to_label: Answer vocabulary mapping
            label_to_answer: Reverse answer vocabulary mapping
            use_wandb: Whether to use Weights & Biases logging
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.answer_to_label = answer_to_label
        self.label_to_answer = label_to_answer

        # Setup optimizer and scheduler
        self.optimizer = self._setup_optimizer()
        self.scheduler = self._setup_scheduler()

        # Training state
        self.current_epoch = 0
        self.global_step = 0
        self.best_val_accuracy = 0.0
        self.best_model_path = None

        # Weights & Biases
        self.use_wandb = use_wandb and WANDB_AVAILABLE
        if self.use_wandb:
            self._init_wandb()

        # Print model info
        print_model_info(self.model)

    def _setup_optimizer(self):
        """Setup optimizer"""
        optimizer = AdamW(
            self.model.parameters(),
            lr=config.training.learning_rate,
            weight_decay=config.training.weight_decay,
        )
        return optimizer

    def _setup_scheduler(self):
        """Setup learning rate scheduler"""
        num_training_steps = len(self.train_loader) * config.training.num_epochs
        scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=config.training.warmup_steps,
            num_training_steps=num_training_steps,
        )
        return scheduler

    def _init_wandb(self):
        """Initialize Weights & Biases"""
        if not WANDB_AVAILABLE:
            print("Warning: wandb not available, skipping logging")
            self.use_wandb = False
            return

        wandb.init(
            project=config.wandb.project_name,
            entity=config.wandb.entity,
            name=config.wandb.run_name
            or f"vqa_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            config=config.to_dict(),
            tags=config.wandb.tags,
        )
        wandb.watch(self.model, log="all", log_freq=100)

    def train_epoch(self, epoch: int):
        """Train for one epoch"""
        self.model.train()
        metrics = VQAMetrics()

        pbar = tqdm(
            self.train_loader, desc=f"Epoch {epoch}/{config.training.num_epochs}"
        )

        for batch_idx, batch in enumerate(pbar):
            # Get batch data
            encoding = batch["encoding"]
            labels = batch["labels"].to(self.device)

            # Move encoding to device
            pixel_values = encoding["pixel_values"].to(self.device)
            input_ids = encoding["input_ids"].to(self.device)
            attention_mask = encoding["attention_mask"].to(self.device)

            # Forward pass
            outputs = self.model(
                pixel_values=pixel_values,
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
            )

            loss = outputs.loss
            # logits not available in generative mode

            # Backward pass
            loss = loss / config.training.gradient_accumulation_steps
            loss.backward()

            # Update weights
            if (batch_idx + 1) % config.training.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), config.training.max_grad_norm
                )
                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()
                self.global_step += 1

            # Compute metrics
            # batch_accuracy = compute_batch_accuracy(logits, answer_labels)
            batch_accuracy = 0.0 # Placeholder

            # Get predictions
            # predictions = torch.argmax(logits, dim=-1)
            # pred_answers = [
            #     self.label_to_answer.get(p.item(), "unknown") for p in predictions
            # ]
            # gt_answers = [
            #     self.label_to_answer.get(label.item(), "unknown")
            #     for label in answer_labels
            # ]

            metrics.update(
                predictions=[], # Empty for now
                ground_truths=[],
                loss=loss.item() * config.training.gradient_accumulation_steps,
            )

            # Update progress bar
            pbar.set_postfix(
                {
                    "loss": f"{loss.item():.4f}",
                    "acc": f"{batch_accuracy:.4f}",
                    "lr": f"{self.scheduler.get_last_lr()[0]:.2e}",
                }
            )

            # Log to wandb
            if self.use_wandb and self.global_step % config.training.logging_steps == 0:
                wandb.log(
                    {
                        "train/loss": loss.item(),
                        "train/accuracy": batch_accuracy,
                        "train/learning_rate": self.scheduler.get_last_lr()[0],
                        "train/epoch": epoch,
                        "train/step": self.global_step,
                    }
                )

        return metrics.compute()

    def validate(self):
        """Validate the model"""
        self.model.eval()
        metrics = VQAMetrics()

        with torch.no_grad():
            pbar = tqdm(self.val_loader, desc="Validation")

            for batch in pbar:
                # Get batch data
                encoding = batch["encoding"]
                labels = batch["labels"].to(self.device)

                # Move encoding to device
                pixel_values = encoding["pixel_values"].to(self.device)
                input_ids = encoding["input_ids"].to(self.device)
                attention_mask = encoding["attention_mask"].to(self.device)

                # Forward pass
                outputs = self.model(
                    pixel_values=pixel_values,
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )

                loss = outputs.loss
                # logits not available in generative mode

                # Compute metrics
                # batch_accuracy = compute_batch_accuracy(logits, answer_labels)
                batch_accuracy = 0.0

                # Get predictions
                # predictions = torch.argmax(logits, dim=-1)
                # pred_answers = [
                #     self.label_to_answer.get(p.item(), "unknown") for p in predictions
                # ]
                # gt_answers = [
                #     self.label_to_answer.get(label.item(), "unknown")
                #     for label in answer_labels
                # ]

                metrics.update(
                    predictions=[], ground_truths=[], loss=loss.item()
                )

                pbar.set_postfix(
                    {"loss": f"{loss.item():.4f}", "acc": f"{batch_accuracy:.4f}"}
                )

        return metrics.compute()

    def train(self):
        """Main training loop"""
        print("\n" + "=" * 60)
        print("Starting Training")
        print("=" * 60)

        start_time = time.time()

        for epoch in range(1, config.training.num_epochs + 1):
            self.current_epoch = epoch

            # Train
            train_metrics = self.train_epoch(epoch)

            # Validate
            val_metrics = self.validate()

            # Print epoch summary
            print(f"\nEpoch {epoch}/{config.training.num_epochs} Summary:")
            print(
                f"  Train Loss: {train_metrics['loss']:.4f} | Train Acc: {train_metrics['accuracy']:.4f}"
            )
            print(
                f"  Val Loss: {val_metrics['loss']:.4f} | Val Acc: {val_metrics['accuracy']:.4f}"
            )

            # Log to wandb
            if self.use_wandb:
                wandb.log(
                    {
                        "val/loss": val_metrics["loss"],
                        "val/accuracy": val_metrics["accuracy"],
                        "epoch": epoch,
                    }
                )

            # Save checkpoint
            if val_metrics["accuracy"] > self.best_val_accuracy:
                self.best_val_accuracy = val_metrics["accuracy"]
                self.save_checkpoint(is_best=True)
                print(f"  ✓ New best model! Accuracy: {self.best_val_accuracy:.4f}")

            # Check if target accuracy reached
            if val_metrics["accuracy"] >= config.training.target_accuracy:
                print(
                    f"\n🎉 Target accuracy {config.training.target_accuracy} reached!"
                )
                break

        # Training complete
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print(f"Total time: {format_time(total_time)}")
        print(f"Best validation accuracy: {self.best_val_accuracy:.4f}")
        print(f"Best model saved to: {self.best_model_path}")

        # Generate model config
        self.generate_model_config()

        if self.use_wandb:
            wandb.finish()

    def save_checkpoint(self, is_best=False):
        """Save model checkpoint"""
        if is_best:
            save_dir = FINAL_MODELS_DIR / "blip_vqa_visually_impaired_v1"
            self.best_model_path = save_dir
        else:
            save_dir = CHECKPOINTS_DIR / f"checkpoint_epoch_{self.current_epoch}"

        save_dir.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(str(save_dir))

        # Save training state
        state = {
            "epoch": self.current_epoch,
            "global_step": self.global_step,
            "best_val_accuracy": self.best_val_accuracy,
            "optimizer_state": self.optimizer.state_dict(),
            "scheduler_state": self.scheduler.state_dict(),
        }
        torch.save(state, save_dir / "training_state.pt")

    def generate_model_config(self):
        """Generate model_config.json for UI development"""
        config_data = {
            "model_info": {
                "name": "blip-vqa-visually-impaired",
                "version": "1.0.0",
                "base_model": config.model.model_name,
                "framework": "pytorch",
                "trained_date": datetime.now().strftime("%Y-%m-%d"),
            },
            "architecture": {
                "vision_encoder": config.model.vision_encoder,
                "text_encoder": config.model.text_encoder,
                "decoder": "GPT-style",
                "hidden_size": config.model.hidden_size,
                "num_attention_heads": config.model.num_attention_heads,
            },
            "preprocessing": {
                "image_size": list(config.model.image_size),
                "normalization": {
                    "mean": list(config.model.image_mean),
                    "std": list(config.model.image_std),
                },
                "text_max_length": config.model.max_text_length,
            },
            "performance": {
                "vqa_accuracy": float(self.best_val_accuracy),
                "target_accuracy": config.training.target_accuracy,
                "model_size_mb": 890,  # Approximate for BLIP-base
            },
            "training": {
                "dataset": "VQA v2",
                "epochs": self.current_epoch,
                "batch_size": config.training.batch_size,
                "learning_rate": config.training.learning_rate,
                "optimizer": config.training.optimizer,
            },
            "api_specification": {
                "input": {"image": "base64 encoded or file path", "question": "string"},
                "output": {"answer": "string", "confidence": "float"},
            },
            "use_cases": [
                "expiry_date_reading",
                "color_identification",
                "object_recognition",
                "text_reading",
                "currency_identification",
            ],
        }

        config_path = OUTPUTS_DIR / "model_config.json"
        save_json(config_data, config_path)

        print(f"\n✓ Model configuration saved to: {config_path}")
        print("  Use this file for mobile app development!")
