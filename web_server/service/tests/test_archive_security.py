import io
import os
import zipfile
import tarfile
import gzip
import bz2
from unittest.mock import patch, MagicMock

import pytest
import rarfile
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from web_server.service.archive_utils import (
    validate_and_sanitize_archive,
    MAX_UNCOMPRESSED_SIZE,
)
from web_server.service.forms import CreateCalibrationForm

MOCK_DICOM = b'\x00' * 128 + b'DICM' + b'DUMMY_DICOM_DATA'


def create_in_memory_zip(files_dict):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in files_dict.items():
            z.writestr(name, content)
    bio.seek(0)
    return ContentFile(bio.read(), name='test.zip')


def create_in_memory_tar(files_dict, compression=''):
    bio = io.BytesIO()
    mode = f'w:{compression}' if compression else 'w'
    with tarfile.open(fileobj=bio, mode=mode) as t:
        for name, content in files_dict.items():
            tarinfo = tarfile.TarInfo(name=name)
            tarinfo.size = len(content)
            t.addfile(tarinfo, io.BytesIO(content))
    bio.seek(0)
    suffix = f'.tar.{compression}' if compression else '.tar'
    return ContentFile(bio.read(), name=f'test{suffix}')


def create_in_memory_gz(content, filename='image.dcm'):
    bio = io.BytesIO()
    with gzip.GzipFile(fileobj=bio, mode='w', filename=filename) as g:
        g.write(content)
    bio.seek(0)
    return ContentFile(bio.read(), name=f'{filename}.gz')


def create_in_memory_bz2(content, filename='image.dcm'):
    bio = io.BytesIO()
    with bz2.BZ2File(bio, 'w') as b:
        b.write(content)
    bio.seek(0)
    return ContentFile(bio.read(), name=f'{filename}.bz2')


def test_valid_zip_extraction():
    files = {
        'image1.dcm': MOCK_DICOM,
        'image2.DCM': MOCK_DICOM,
        'ignored.txt': b'some text description',
    }
    uploaded = create_in_memory_zip(files)
    result = validate_and_sanitize_archive(uploaded)

    assert result.name == 'test.zip'
    # Verify the repacked zip
    with zipfile.ZipFile(result) as z:
        namelist = z.namelist()
        assert 'image1.dcm' in namelist
        assert 'image2.DCM' in namelist
        assert 'ignored.txt' not in namelist
        assert z.read('image1.dcm') == MOCK_DICOM


def test_valid_tar_gz_extraction():
    files = {
        'subdir/image.dcm': MOCK_DICOM,
        'ignored.txt': b'some text description',
    }
    uploaded = create_in_memory_tar(files, compression='gz')
    result = validate_and_sanitize_archive(uploaded)

    assert result.name == 'test.zip'
    with zipfile.ZipFile(result) as z:
        namelist = z.namelist()
        assert 'subdir/image.dcm' in namelist
        assert 'ignored.txt' not in namelist
        assert z.read('subdir/image.dcm') == MOCK_DICOM


def test_valid_tar_bz2_extraction():
    files = {
        'image.dcm': MOCK_DICOM,
    }
    uploaded = create_in_memory_tar(files, compression='bz2')
    result = validate_and_sanitize_archive(uploaded)

    assert result.name == 'test.zip'
    with zipfile.ZipFile(result) as z:
        assert 'image.dcm' in z.namelist()


def test_valid_gzip_single_file():
    uploaded = create_in_memory_gz(MOCK_DICOM, filename='patient1.dcm')
    result = validate_and_sanitize_archive(uploaded)

    assert result.name == 'patient1.dcm.zip'
    with zipfile.ZipFile(result) as z:
        assert 'patient1.dcm' in z.namelist()
        assert z.read('patient1.dcm') == MOCK_DICOM


def test_valid_bzip2_single_file():
    uploaded = create_in_memory_bz2(MOCK_DICOM, filename='patient2.dcm')
    result = validate_and_sanitize_archive(uploaded)

    assert result.name == 'patient2.dcm.zip'
    with zipfile.ZipFile(result) as z:
        assert 'patient2.dcm' in z.namelist()
        assert z.read('patient2.dcm') == MOCK_DICOM


def test_invalid_unsupported_format():
    uploaded = ContentFile(b'7z\xbc\xaf\x27\x1c' + b'\x00' * 1000, name='test.7z')
    with pytest.raises(ValidationError) as excinfo:
        validate_and_sanitize_archive(uploaded)
    assert "Formato de arquivo compactado não suportado ou inválido." in str(excinfo.value)


def test_corrupted_zip():
    uploaded = ContentFile(b'PK\x03\x04' + b'\x00' * 1000, name='corrupted.zip')
    with pytest.raises(ValidationError) as excinfo:
        validate_and_sanitize_archive(uploaded)
    assert "Invalid or corrupted zip archive" in str(excinfo.value)


def test_zip_slip_prevention():
    files = {
        '../../etc/passwd': MOCK_DICOM,
        '/absolute/path/image.dcm': MOCK_DICOM,
    }
    uploaded = create_in_memory_zip(files)
    with pytest.raises(ValidationError) as excinfo:
        validate_and_sanitize_archive(uploaded)
    assert "Path traversal attack detected" in str(excinfo.value) or "Invalid path" in str(excinfo.value)


def test_decompression_bomb_prevention():
    files = {
        'huge1.dcm': b'\x00' * 200,
    }
    uploaded = create_in_memory_zip(files)
    # Temporarily set MAX_UNCOMPRESSED_SIZE to 100 bytes to trigger protection
    with patch('web_server.service.archive_utils.MAX_UNCOMPRESSED_SIZE', 100):
        with pytest.raises(ValidationError) as excinfo:
            validate_and_sanitize_archive(uploaded)
        assert "Decompression limit exceeded" in str(excinfo.value)


def test_empty_archive():
    files = {
        'ignored.txt': b'no dicom here',
    }
    uploaded = create_in_memory_zip(files)
    with pytest.raises(ValidationError) as excinfo:
        validate_and_sanitize_archive(uploaded)
    assert "O arquivo compactado não contém imagens DICOM válidas." in str(excinfo.value)


@patch('rarfile.RarFile')
def test_valid_rar_extraction(mock_rarfile):
    # Mocking RarInfo objects
    mock_info = MagicMock()
    mock_info.filename = 'image.dcm'
    mock_info.file_size = len(MOCK_DICOM)
    mock_info.isdir.return_value = False

    # Configure the RarFile mock instance
    mock_instance = MagicMock()
    mock_instance.infolist.return_value = [mock_info]
    mock_instance.open.return_value.__enter__.return_value.read.side_effect = [MOCK_DICOM, b'']
    mock_rarfile.return_value.__enter__.return_value = mock_instance

    # Mock the magic byte detection by passing header bytes corresponding to Rar
    uploaded = ContentFile(b'Rar!\x1a\x07\x00' + b'\x00' * 1000, name='test.rar')
    result = validate_and_sanitize_archive(uploaded)

    assert result.name == 'test.zip'
    with zipfile.ZipFile(result) as z:
        assert 'image.dcm' in z.namelist()
        assert z.read('image.dcm') == MOCK_DICOM


@pytest.mark.django_db
def test_form_validation_integration(calibration_infos):
    # Test valid zip upload through form
    files = {'images': create_in_memory_zip({'slice.dcm': MOCK_DICOM})}
    form = CreateCalibrationForm(data=calibration_infos, files=files)
    assert form.is_valid()

    # Test invalid zip upload through form (no DICOM)
    files_invalid = {'images': create_in_memory_zip({'dummy.txt': b'hello'})}
    form_invalid = CreateCalibrationForm(data=calibration_infos, files=files_invalid)
    assert not form_invalid.is_valid()
    assert 'images' in form_invalid.errors
    assert "O arquivo compactado não contém imagens DICOM válidas." in form_invalid.errors['images'][0]
