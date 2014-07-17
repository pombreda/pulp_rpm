import os
from xml.dom import pulldom

from pulp.plugins.util.metadata_writer import FastForwardXmlFileContext

from pulp_rpm.plugins.distributors.yum.metadata.metadata import REPO_DATA_DIR_NAME


FILE_LISTS_XML_FILE_NAME = 'filelists.xml.gz'
FILE_LISTS_NAMESPACE = 'http://linux.duke.edu/metadata/filelists'


class FilelistsXMLFileContext(FastForwardXmlFileContext):
    """
    Context manager for generating the filelists.xml.gz file.
    """

    def __init__(self, working_dir, num_units, checksum_type=None):
        """
        :param working_dir: working directory to create the filelists.xml.gz in
        :type  working_dir: str
        :param num_units: total number of units whose metadata will be written
                          into the filelists.xml.gz metadata file, or the number of packages added
        :type  num_units: int
        """

        metadata_file_path = os.path.join(working_dir, REPO_DATA_DIR_NAME, FILE_LISTS_XML_FILE_NAME)
        self.num_packages = num_units
        attributes = {'xmlns': FILE_LISTS_NAMESPACE,
                      'packages': str(self.num_packages)}
        super(FilelistsXMLFileContext, self).__init__(metadata_file_path, 'filelists',
                                                      root_attributes=attributes,
                                                      checksum_type=checksum_type)

    def initialize(self):
        """
        Initialize all the file handles and fast forward the xml to the point where we should
        start adding content
        """
        super(FilelistsXMLFileContext, self).initialize()
        # Fast Forward to where we can start writing
        if self.fast_forward:
            for event in self.xml_generator:
                if event[0] == pulldom.START_ELEMENT and event[1].nodeName == 'filelists':
                    # Get the current packages count and add it to the previous
                    package_count = int(event[1].attributes['packages'].value)
                    package_count += self.num_packages
                    event[1].attributes['packages'].value = str(package_count)
                elif event[0] == pulldom.END_ELEMENT and event[1].nodeName == 'filelists':
                    # break out and insert more stuff here
                    break

    def add_unit_metadata(self, unit):
        """
        Add the metadata to the xml file for the given unit.

        :param unit: unit whose metadata is to be written
        :type  unit: pulp.plugins.model.Unit
        """
        metadata = unit.metadata['repodata']['filelists']
        self.metadata_file_handle.write(metadata)

