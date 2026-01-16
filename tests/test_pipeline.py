"""Tests for modules/pipeline.py - Pipeline architecture."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from modules.pipeline import (
    CleanupStage,
    DiarizeStage,
    PipelineStage,
    TranscribeStage,
    TranscriptionPipeline,
    create_default_pipeline,
)
from modules.types import DiarizedSegment
from modules.transcriber import TranscriptSegment


class TestPipelineStage:
    """Tests for PipelineStage abstract base class."""

    def test_cannot_instantiate_directly(self):
        """Test that PipelineStage cannot be instantiated."""
        with pytest.raises(TypeError):
            PipelineStage()

    def test_subclass_must_implement_name(self):
        """Test that subclasses must implement name property."""

        class IncompleteStageMissingName(PipelineStage):
            def process(self, data):
                return data

        with pytest.raises(TypeError):
            IncompleteStageMissingName()

    def test_subclass_must_implement_process(self):
        """Test that subclasses must implement process method."""

        class IncompleteStageMissingProcess(PipelineStage):
            @property
            def name(self):
                return "Test"

        with pytest.raises(TypeError):
            IncompleteStageMissingProcess()

    def test_complete_subclass_works(self):
        """Test that complete subclass can be instantiated."""

        class CompleteStage(PipelineStage):
            @property
            def name(self):
                return "Complete"

            def process(self, data):
                return data

        stage = CompleteStage()
        assert stage.name == "Complete"
        assert stage.process("test") == "test"


class TestTranscribeStage:
    """Tests for TranscribeStage class."""

    def test_name_property(self):
        """Test that name is 'Transcribe'."""
        stage = TranscribeStage()
        assert stage.name == "Transcribe"

    def test_inherits_from_pipeline_stage(self):
        """Test that TranscribeStage inherits from PipelineStage."""
        assert issubclass(TranscribeStage, PipelineStage)

    def test_default_settings(self):
        """Test default settings."""
        stage = TranscribeStage()
        assert stage._use_gpu is True
        assert stage._show_progress is True
        assert stage._debug is False

    def test_custom_settings(self):
        """Test custom settings."""
        stage = TranscribeStage(
            use_gpu=False,
            show_progress=False,
            debug=True,
            model_size="medium",
        )
        assert stage._use_gpu is False
        assert stage._show_progress is False
        assert stage._debug is True
        assert stage._model_size == "medium"


class TestDiarizeStage:
    """Tests for DiarizeStage class."""

    def test_name_property(self):
        """Test that name is 'Diarize'."""
        stage = DiarizeStage()
        assert stage.name == "Diarize"

    def test_inherits_from_pipeline_stage(self):
        """Test that DiarizeStage inherits from PipelineStage."""
        assert issubclass(DiarizeStage, PipelineStage)

    def test_default_enabled(self):
        """Test that diarization is enabled by default."""
        stage = DiarizeStage()
        assert stage._enabled is True

    def test_can_be_disabled(self):
        """Test that diarization can be disabled."""
        stage = DiarizeStage(enabled=False)
        assert stage._enabled is False

    def test_set_audio_path(self):
        """Test setting audio path."""
        stage = DiarizeStage()
        result = stage.set_audio_path("/path/to/audio.mp4")

        assert stage._audio_path == Path("/path/to/audio.mp4")
        assert result is stage  # Returns self for chaining

    def test_process_when_disabled(self, sample_transcript_segments):
        """Test that disabled stage returns segments without speakers."""
        stage = DiarizeStage(enabled=False)

        result = stage.process(sample_transcript_segments)

        assert len(result) == len(sample_transcript_segments)
        assert all(isinstance(seg, DiarizedSegment) for seg in result)
        assert all(seg.speaker == "Speaker" for seg in result)


class TestCleanupStage:
    """Tests for CleanupStage class."""

    def test_name_property(self):
        """Test that name is 'Cleanup'."""
        stage = CleanupStage()
        assert stage.name == "Cleanup"

    def test_inherits_from_pipeline_stage(self):
        """Test that CleanupStage inherits from PipelineStage."""
        assert issubclass(CleanupStage, PipelineStage)

    def test_default_enabled(self):
        """Test that cleanup is enabled by default."""
        stage = CleanupStage()
        assert stage._enabled is True

    def test_can_be_disabled(self):
        """Test that cleanup can be disabled."""
        stage = CleanupStage(enabled=False)
        assert stage._enabled is False

    def test_process_when_disabled(self, sample_diarized_segments):
        """Test that disabled stage returns segments unchanged."""
        stage = CleanupStage(enabled=False)

        result = stage.process(sample_diarized_segments)

        assert result == sample_diarized_segments

    def test_process_removes_hallucinations(self, segments_with_hallucinations):
        """Test that cleanup removes hallucinations."""
        stage = CleanupStage(
            remove_hallucinations=True,
            remove_duplicates=False,
            remove_fillers=False,
            remove_non_english=False,
            min_segment_length=0,
        )

        result = stage.process(segments_with_hallucinations)

        # Should remove "Thanks for watching", "Don't forget to subscribe", "[music]"
        assert len(result) == 2
        texts = [seg.text for seg in result]
        assert "This is real content." in texts
        assert "More real content here." in texts

    def test_custom_settings(self):
        """Test custom cleanup settings."""
        stage = CleanupStage(
            remove_duplicates=False,
            remove_fillers=False,
            min_segment_length=10,
            similarity_threshold=0.8,
        )

        assert stage._remove_duplicates is False
        assert stage._remove_fillers is False
        assert stage._min_segment_length == 10
        assert stage._similarity_threshold == 0.8


class TestTranscriptionPipeline:
    """Tests for TranscriptionPipeline class."""

    def test_empty_pipeline(self):
        """Test creating empty pipeline."""
        pipeline = TranscriptionPipeline()
        assert len(pipeline.stages) == 0

    def test_add_stage(self):
        """Test adding a stage."""
        pipeline = TranscriptionPipeline()
        stage = CleanupStage()

        result = pipeline.add_stage(stage)

        assert len(pipeline.stages) == 1
        assert pipeline.stages[0] is stage
        assert result is pipeline  # Returns self for chaining

    def test_fluent_api(self):
        """Test fluent API for adding multiple stages."""
        pipeline = (
            TranscriptionPipeline()
            .add_stage(TranscribeStage())
            .add_stage(DiarizeStage())
            .add_stage(CleanupStage())
        )

        assert len(pipeline.stages) == 3
        assert pipeline.stages[0].name == "Transcribe"
        assert pipeline.stages[1].name == "Diarize"
        assert pipeline.stages[2].name == "Cleanup"

    def test_stages_property_returns_copy(self):
        """Test that stages property returns a copy."""
        pipeline = TranscriptionPipeline()
        pipeline.add_stage(CleanupStage())

        stages = pipeline.stages
        stages.append(DiarizeStage())

        # Original should be unchanged
        assert len(pipeline.stages) == 1

    def test_on_stage_start_callback(self):
        """Test setting stage start callback."""
        pipeline = TranscriptionPipeline()
        callback = MagicMock()

        result = pipeline.on_stage_start(callback)

        assert pipeline._on_stage_start is callback
        assert result is pipeline

    def test_on_stage_complete_callback(self):
        """Test setting stage complete callback."""
        pipeline = TranscriptionPipeline()
        callback = MagicMock()

        result = pipeline.on_stage_complete(callback)

        assert pipeline._on_stage_complete is callback
        assert result is pipeline


class TestCreateDefaultPipeline:
    """Tests for create_default_pipeline factory function."""

    def test_creates_pipeline(self):
        """Test that function creates a TranscriptionPipeline."""
        pipeline = create_default_pipeline()

        assert isinstance(pipeline, TranscriptionPipeline)

    def test_has_three_stages(self):
        """Test that default pipeline has three stages."""
        pipeline = create_default_pipeline()

        assert len(pipeline.stages) == 3

    def test_stages_in_correct_order(self):
        """Test that stages are in correct order."""
        pipeline = create_default_pipeline()

        assert pipeline.stages[0].name == "Transcribe"
        assert pipeline.stages[1].name == "Diarize"
        assert pipeline.stages[2].name == "Cleanup"

    def test_disable_diarization(self):
        """Test creating pipeline with diarization disabled."""
        pipeline = create_default_pipeline(enable_diarization=False)

        diarize_stage = pipeline.stages[1]
        assert diarize_stage._enabled is False

    def test_disable_cleanup(self):
        """Test creating pipeline with cleanup disabled."""
        pipeline = create_default_pipeline(enable_cleanup=False)

        cleanup_stage = pipeline.stages[2]
        assert cleanup_stage._enabled is False

    def test_with_config(self):
        """Test creating pipeline with config."""
        from modules.config import TranscribeConfig

        config = TranscribeConfig(model="medium")
        pipeline = create_default_pipeline(config=config)

        transcribe_stage = pipeline.stages[0]
        assert transcribe_stage._config is config


class TestPipelineExecution:
    """Tests for pipeline execution with mocked stages."""

    def test_simple_pipeline_execution(self):
        """Test executing a simple custom pipeline."""

        class DoubleStage(PipelineStage):
            @property
            def name(self):
                return "Double"

            def process(self, data):
                return data * 2

        class AddOneStage(PipelineStage):
            @property
            def name(self):
                return "AddOne"

            def process(self, data):
                return data + 1

        pipeline = (
            TranscriptionPipeline()
            .add_stage(DoubleStage())
            .add_stage(AddOneStage())
        )

        # Mock the run method to accept non-Path input for testing
        # (5 * 2) + 1 = 11
        result = 5
        for stage in pipeline.stages:
            result = stage.process(result)

        assert result == 11

    def test_callbacks_called_in_order(self):
        """Test that callbacks are called during execution."""
        start_calls = []
        complete_calls = []

        class PassthroughStage(PipelineStage):
            def __init__(self, stage_name):
                self._name = stage_name

            @property
            def name(self):
                return self._name

            def process(self, data):
                return data

        pipeline = (
            TranscriptionPipeline()
            .add_stage(PassthroughStage("Stage1"))
            .add_stage(PassthroughStage("Stage2"))
            .on_stage_start(lambda name: start_calls.append(name))
            .on_stage_complete(lambda name, data: complete_calls.append(name))
        )

        # Manually execute stages to test callbacks
        data = "initial"
        for stage in pipeline.stages:
            if pipeline._on_stage_start:
                pipeline._on_stage_start(stage.name)
            data = stage.process(data)
            if pipeline._on_stage_complete:
                pipeline._on_stage_complete(stage.name, data)

        assert start_calls == ["Stage1", "Stage2"]
        assert complete_calls == ["Stage1", "Stage2"]
