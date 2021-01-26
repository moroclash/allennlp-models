from transformers import AutoModel

from allennlp.common.testing import ModelTestCase
from allennlp.data import Vocabulary
from allennlp.common.testing import assert_equal_parameters

from tests import FIXTURES_ROOT


class TestVEVilbert(ModelTestCase):
    def test_model_can_train_save_and_load_small_model(self):
        param_file = FIXTURES_ROOT / "vision" / "vilbert_ve" / "experiment.jsonnet"
        self.ensure_model_can_train_save_and_load(param_file)

    def test_model_can_train_save_and_load_with_cache(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix=self.__class__.__name__) as d:
            overrides = {"dataset_reader": {"feature_cache_dir": str(d)}}
            import json

            overrides = json.dumps(overrides)
            param_file = FIXTURES_ROOT / "vision" / "vilbert_ve" / "experiment.jsonnet"
            self.ensure_model_can_train_save_and_load(param_file, overrides=overrides)

    def test_model_can_train_save_and_load_from_huggingface(self):
        param_file = FIXTURES_ROOT / "vision" / "vilbert_ve" / "experiment_from_huggingface.jsonnet"
        self.ensure_model_can_train_save_and_load(param_file)

    def test_model_loads_weights_correctly(self):
        from allennlp_models.vision.models.visual_entailment import VisualEntailmentModel

        vocab = Vocabulary()
        model_name = "epwalsh/bert-xsmall-dummy"
        model = VisualEntailmentModel.from_huggingface_model_name(
            vocab=vocab,
            model_name=model_name,
            image_feature_dim=2048,
            image_num_hidden_layers=1,
            image_hidden_size=3,
            image_num_attention_heads=1,
            combined_num_attention_heads=1,
            combined_hidden_size=5,
            pooled_output_dim=7,
            image_intermediate_size=11,
            image_attention_dropout=0.0,
            image_hidden_dropout=0.0,
            image_biattention_id=[0, 1],
            text_biattention_id=[0, 1],
            text_fixed_layer=0,
            image_fixed_layer=0,
        )

        transformer = AutoModel.from_pretrained(model_name)

        # compare embedding parameters
        mapping = {
            val: key
            for key, val in model.backbone.text_embeddings._construct_default_mapping(
                transformer.embeddings, "huggingface", {}
            ).items()
        }
        assert_equal_parameters(
            transformer.embeddings, model.backbone.text_embeddings, mapping=mapping
        )

        # compare encoder parameters
        mapping = {
            val: key
            for key, val in model.backbone.encoder._construct_default_mapping(
                transformer.encoder, "huggingface", {}
            ).items()
        }

        # We ignore the new parameters for the second modality, since they won't be present
        # in the huggingface model.
        assert_equal_parameters(
            transformer.encoder, model.backbone.encoder, ignore_missing=True, mapping=mapping
        )
