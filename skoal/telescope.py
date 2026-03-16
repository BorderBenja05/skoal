import numpy as np
from skoal.tesselation_generator import make_tiling


class Telescope:
    """A telescope with a defined sky tessellation and observing constraints.

    Parameters
    ----------
    name : str
        Telescope identifier (used in output and observer labelling).
    lat : float
        Geodetic latitude in degrees (positive north).
    lon : float
        Geodetic longitude in degrees (positive east).
    elevation : float
        Elevation above sea level in metres.
    ra_fov : float
        Instrument field-of-view width (RA direction) in degrees.
    dec_fov : float
        Instrument field-of-view height (Dec direction) in degrees.
    scale : float
        Tile overlap scale factor. 1.0 = exact FOV, <1.0 = slight overlap
        (default 0.98).
    horizon : float or callable
        Minimum observable altitude in degrees. Pass a callable
        ``f(az_deg: float) -> float`` for an azimuth-dependent profile,
        e.g. ``lambda az: 20 if 90 < az < 270 else 10`` (default 10.0).

    Examples
    --------
    Basic usage::

        import skoal

        scope = skoal.Telescope(
            name='RASA11',
            lat=45.0, lon=-93.1, elevation=1000,
            ra_fov=3.2, dec_fov=2.1,
        )

        # Rank fields for a gravitational-wave event
        fields = scope.rank_lvc('path/to/bayestar.fits', min_prob=0.90)

        # Filter to what is actually up tonight
        visible = scope.filter_observable(fields)

    Azimuth-dependent horizon::

        scope = skoal.Telescope(
            name='MyScope',
            lat=34.0, lon=-117.0, elevation=500,
            ra_fov=1.0, dec_fov=1.0,
            horizon=lambda az: 25 if 200 < az < 340 else 15,
        )
    """

    def __init__(self, name, lat, lon, elevation, ra_fov, dec_fov,
                 scale=0.98, horizon=10.0):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.elevation = elevation
        self.ra_fov = ra_fov
        self.dec_fov = dec_fov
        self.scale = scale
        self.horizon = horizon
        self._tiling = None

    # ------------------------------------------------------------------
    # Tiling
    # ------------------------------------------------------------------

    @property
    def tiling(self):
        """numpy.ndarray (N, 3) — sky tessellation [field_id, ra_deg, dec_deg].
        Generated once on first access and cached.
        """
        if self._tiling is None:
            self._tiling = make_tiling(self.ra_fov, self.dec_fov, self.scale)
        return self._tiling

    def regenerate_tiling(self, scale=None):
        """Force regeneration of the tessellation (e.g. after changing scale).

        Parameters
        ----------
        scale : float or None
            New scale factor. If None, uses ``self.scale``.
        """
        if scale is not None:
            self.scale = scale
        self._tiling = make_tiling(self.ra_fov, self.dec_fov, self.scale)
        return self._tiling

    # ------------------------------------------------------------------
    # Field ranking
    # ------------------------------------------------------------------

    def rank_lvc(self, skymap_path, min_prob=0.90):
        """Rank tessellation fields by LVC/GW skymap probability.

        Parameters
        ----------
        skymap_path : str or Path
            Path to a multi-order FITS skymap (e.g. bayestar.multiorder.fits).
        min_prob : float
            Cumulative probability threshold. Only pixels inside the
            ``min_prob`` credible region are considered (default 0.90).

        Returns
        -------
        list of (field_id, ra_deg, dec_deg, probability)
            Sorted highest-probability first.
        """
        from skoal.lvc_handler import generate_fields_from_skymap
        sorted_fields, ids_to_fields = generate_fields_from_skymap(
            skymap_path, self.ra_fov, self.dec_fov, self.scale, min_prob
        )
        return [
            (fid, float(np.rad2deg(ids_to_fields[fid][0])),
             float(np.rad2deg(ids_to_fields[fid][1])), float(prob))
            for fid, prob in sorted_fields
        ]

    def rank_fermi(self, ra, dec, error):
        """Find tessellation fields within a FERMI GBM error circle.

        Parameters
        ----------
        ra : float
            FERMI event RA in degrees.
        dec : float
            FERMI event Dec in degrees.
        error : float
            FERMI error radius in degrees.

        Returns
        -------
        list of (field_id, ra_deg, dec_deg, probability)
            Fields within the (buffered) error circle, probability = 1.0.
        """
        from skoal.Fermi_handler import fields_in_error_circle
        return fields_in_error_circle(
            self.tiling, ra, dec, error, self.ra_fov, self.dec_fov
        )

    def rank_fermi_voevent(self, voevent_path):
        """Convenience wrapper: parse a FERMI VOEvent file then call rank_fermi.

        Parameters
        ----------
        voevent_path : str or Path
            Path to a FERMI GBM VOEvent XML file.

        Returns
        -------
        list of (field_id, ra_deg, dec_deg, probability)
        """
        from skoal.GCN_utils import getFERMICoordinates
        ra, dec, error = getFERMICoordinates(str(voevent_path))
        return self.rank_fermi(ra, dec, error)

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    def filter_observable(self, fields, time=None, horizon=None):
        """Filter a field list to targets observable from this telescope.

        Parameters
        ----------
        fields : list of tuples
            Each tuple must start with (field_id, ra_deg, dec_deg, ...).
        time : astropy.time.Time or None
            Observation time. Defaults to now + 12 h.
        horizon : float, callable, or None
            Override the telescope's default horizon for this call.
            Accepts the same forms as the ``horizon`` constructor argument.

        Returns
        -------
        list
            Observable subset of *fields*.
        """
        from skoal.scheduler_utilities import filter_for_visibility
        h = horizon if horizon is not None else self.horizon
        return filter_for_visibility(
            fields, self.lat, self.lon, self.elevation,
            self.name, horizon=h, time=time
        )

    # ------------------------------------------------------------------
    # Multi-telescope splitting
    # ------------------------------------------------------------------

    def split(self, fields, n):
        """Divide a field list across *n* telescopes using spatial clustering.

        Parameters
        ----------
        fields : list of tuples
            Each tuple starts with (field_id, ra_deg, dec_deg, ...).
        n : int
            Number of telescopes (sub-lists) to create.

        Returns
        -------
        list of lists
            *n* lists, each a spatially compact subset of *fields*.
        """
        from skoal.scheduler_utilities import (
            separate_targets_into_clusters, separate_targets_evenly
        )
        if n == 1:
            return [fields]
        try:
            return separate_targets_into_clusters(fields, n)
        except Exception:
            return separate_targets_evenly(fields, n)

    def __repr__(self):
        return (f"Telescope(name={self.name!r}, lat={self.lat}, lon={self.lon}, "
                f"ra_fov={self.ra_fov}°, dec_fov={self.dec_fov}°)")
