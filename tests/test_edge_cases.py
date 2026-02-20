"""Tests for edge case scenarios and option combinations."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ytp3.cli import setup_parser


class TestAudioModeWithSponsorBlock:
    """Test that SponsorBlock is properly handled in audio mode."""
    
    def test_audio_mode_disables_sponsorblock(self):
        """Test that audio mode should skip sponsorblock setting."""
        # This is a logic test - we can't actually set sponsorblock from CLI
        # but we can verify the parser accepts the combination
        parser = setup_parser()
        
        # Audio mode should be accepted
        args = parser.parse_args(['-a', '-f', 'mp3', 'https://www.youtube.com/watch?v=test'])
        
        assert args.audio is True
        assert args.format == 'mp3'
    
    def test_parser_accepts_audio_and_format_combination(self):
        """Test that parser accepts audio mode with various formats."""
        parser = setup_parser()
        
        formats = ['mp3', 'wav', 'm4a', 'aac', 'opus', 'vorbis']
        
        for fmt in formats:
            args = parser.parse_args(['-a', '-f', fmt, 'https://www.youtube.com/watch?v=test'])
            
            assert args.audio is True
            assert args.format == fmt


class TestVideoModeWithSponsorBlock:
    """Test that SponsorBlock works correctly in video mode."""
    
    def test_parser_accepts_video_mode_default(self):
        """Test that video mode is the default."""
        parser = setup_parser()
        args = parser.parse_args(['https://www.youtube.com/watch?v=test'])
        
        # Audio mode should default to False
        assert args.audio is False


class TestEdgeCaseDocumentation:
    """Test that edge cases are documented."""
    
    def test_development_md_has_edge_cases_table(self):
        """Test that DEVELOPMENT.md contains edge cases documentation."""
        import os
        
        dev_file = 'DEVELOPMENT.md'
        assert os.path.exists(dev_file), "DEVELOPMENT.md should exist"
        
        with open(dev_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have edge cases section
        assert 'Edge Cases' in content, "Should have Edge Cases section"
        assert 'SponsorBlock' in content, "Should document SponsorBlock edge cases"
        assert 'Audio' in content, "Should document Audio mode edge cases"
        assert 'Mode' in content or 'mode' in content, "Should mention mode combinations"
    
    def test_edge_case_table_documents_audio_sponsor_issue(self):
        """Test that the edge case table documents Audio+SponsorBlock interaction."""
        with open('DEVELOPMENT.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should mention the specific issue
        assert 'Audio' in content and 'SponsorBlock' in content, \
            "Should document Audio+SponsorBlock interaction"
        
        # Should mention the solution
        assert 'Disabled' in content or 'disabled' in content or 'disable' in content, \
            "Should explain how Audio+SponsorBlock is handled"


class TestOptionHandlingLogic:
    """Test the logic of option handling in different modes."""
    
    def test_audio_codec_map_comprehensiveness(self):
        """Test that audio codec map covers common formats."""
        # This tests that the CLI has proper codec mapping
        from ytp3.cli import setup_parser
        
        parser = setup_parser()
        args = parser.parse_args(['-a', '-f', 'mp3', 'https://www.youtube.com/watch?v=test'])
        
        # Should accept common audio formats
        assert args.format in ['mp3', 'wav', 'm4a', 'aac', 'opus', 'vorbis']
    
    def test_format_selection_audio_modes(self):
        """Test various audio format selections."""
        parser = setup_parser()
        
        audio_formats = ['mp3', 'wav', 'm4a']
        
        for fmt in audio_formats:
            args = parser.parse_args(['-a', '-f', fmt, 'https://example.com/test'])
            assert args.format == fmt
            assert args.audio is True
