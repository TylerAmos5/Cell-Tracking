"""Functions to read in an ND2 file with multiple channels and sites

    * read_nd2 - read in an ND2 file with multiple channels and sites
                and output a dictionary with pixel values for each
                site/frame/channel
    * get_channel_rawData - return pixel values for a given
                site/frame/channel in a 2022 x 2044 array
    * get_frame_data - return a dictionary of pixels for all channels
                for a given site/frame
    * get_site_data - return a dictionary of pixels for all frames and
            channels for a given site
"""

import nd2reader
import numpy as np


def read_nd2(nd2_filename):
    """Read in an ND2 file with multiple channels and sites and output a
            dictionary with pixel values for each site/frame/channel.

    Parameters
    ----------
    nd2_filename: File name for nd2 file that comes from XXXX microscope
                    (edits may be necessary if ND2 file structure differs).
                    The main repo directory for this file will be specified
                    using a separate function, so this parameter should only
                    include the file path from the main repo.

    Returns
    -------
    well_data: a dictionary with the format:
                well --> site --> frame[channels]
                frame contains one 2048 x 2044 2D array for each channel,
                    with values for each of the pixels
                the components of this dictionary can be accessed using:
                    well_data[site][frame][channel]
    """
    try:
        with nd2reader.ND2Reader(nd2_filename) as nd2_movie:
            nd2_movie.iter_axes = 'v'
            well_data = {}
            for fov in range(nd2_movie.sizes['v']):
                frame_data = {}
                nd2_movie.iter_axes = 't'
                for f in range(nd2_movie.sizes['t']):
                    nd2_movie.iter_axes = 'c'
                    channel_data = []
                    for c in range(nd2_movie.sizes['c']):
                        nd2_movie.default_coords['v'] = fov
                        nd2_movie.default_coords['t'] = f
                        nd2_movie.default_coords['c'] = c
                        channel_data.append(nd2_movie[c])

                    channel_data = np.array(channel_data)
                    channel_data = channel_data.transpose((1, 2, 0))
                    frame_data[f] = channel_data
                well_data[fov] = frame_data
    except nd2reader.exceptions.InvalidFileType:
        print("Invalid file type: " + nd2_filename)
        raise nd2reader.exceptions.InvalidFileType
    except FileNotFoundError:
        print("File not found: " + nd2_filename)
        well_data = None
        raise FileNotFoundError
    return well_data


def get_channel_rawData(well_data, site, frame, channel):
    """Return pixel values for a given site/frame/channel in
            a 2048 x 2044 array.

    Parameters
    ----------
    well_data: a dictionary with the format:
                well --> site --> frame[channels]
                frame contains one 2048 x 2044 2D array for each channel,
                    with values for each of the pixels
                the components of this dictionary can be accessed using:
                    well_data[site][frame][channel]
    site: site number (0 or 1)
    frame: frame number
    channel: channel number (0, 1, or 2)

    Returns
    -------
    well_data[site][frame][:, :, channel]: a 2048 x 2044 2D array for the
                                            specified site/frame/channel
                                            with values for each of the pixels
    """
    try:
        return well_data[site][frame][:, :, channel]
    except IndexError:
        print("Invalid site/frame/channel combination: " + str(site) + "/"
              + str(frame) + "/" + str(channel))
        raise
    except KeyError:
        print("Invalid site/frame/channel combination: " + str(site) + "/"
              + str(frame) + "/" + str(channel))
        raise


def get_frame_data(well_data, site, frame):
    """Return a dictionary of pixels for all channels for a given site/frame.

    Parameters
    ----------
    well_data: a dictionary with the format:
                well --> site --> frame[channels]
                frame contains one 2048 x 2044 2D array for each channel,
                    with values for each of the pixels
                the components of this dictionary can be accessed using:
                    well_data[site][frame][channel]
    site: site number (0 or 1)
    frame: frame number

    Returns
    -------
    well_data[site][frame]: a dictionary of 2048 x 2044 2D arrays for the
                                specified site/frame for all channels
                                with values for each of the pixels
    """
    try:
        return well_data[site][frame]
    except KeyError:
        print("Invalid site/frame combination: " + str(site) + "/"
              + str(frame))
        raise KeyError


def get_site_data(well_data, site):
    """Return a dictionary of pixels for all frames and
            channels for a given site.

    Parameters
    ----------
    well_data: a dictionary with the format:
                well --> site --> frame[channels]
                frame contains one 2048 x 2044 2D array for each channel,
                    with values for each of the pixels
                the components of this dictionary can be accessed using:
                    well_data[site][frame][channel]
    site: site number (0 or 1)

    Returns
    -------
    well_data[site]: a dictionary of 2048 x 2044 2D arrays for the
                        specified site with the format
                        site --> frame[channel]
    """
    try:
        return well_data[site]
    except KeyError:
        print("Invalid site: " + str(site))
        raise
