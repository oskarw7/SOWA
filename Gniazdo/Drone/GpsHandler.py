import math
from datetime import datetime


class GpsHandler:
    # WGS84 Earth radius
    R = 6378137.0

    def __init__(self, lat0=51, lon0=51, alt0=0):
        """
        Initialize with reference GPS point.

        lat0, lon0 in degrees
        alt0 in meters
        """
        self.lat0 = lat0
        self.lon0 = lon0
        self.alt0 = alt0
        self.lat0_rad = math.radians(lat0)

    def enu_to_geodetic(self, x_east, y_north, z_up):
        """
        Convert ENU offset (meters) to geodetic coordinates.
        """
        dlat = y_north / self.R
        dlon = x_east / (self.R * math.cos(self.lat0_rad))

        lat = self.lat0 + math.degrees(dlat)
        lon = self.lon0 + math.degrees(dlon)
        alt = self.alt0 + z_up

        return lat, lon, alt

    def _decimal_to_nmea(self, coord, is_lat=True):
        """
        Convert decimal degrees to NMEA format.
        """
        if is_lat:
            hemisphere = "N" if coord >= 0 else "S"
            degrees = int(abs(coord))
            minutes = (abs(coord) - degrees) * 60
            return f"{degrees:02d}{minutes:07.4f}", hemisphere
        else:
            hemisphere = "E" if coord >= 0 else "W"
            degrees = int(abs(coord))
            minutes = (abs(coord) - degrees) * 60
            return f"{degrees:03d}{minutes:07.4f}", hemisphere

    def generate_nema_gga(
        self, x_east, y_north, z_up, fix_quality=1, num_sat=8, hdop=0.9
    ):
        """
        Convert ENU → NMEA GGA sentence directly.
        """
        lat, lon, alt = self.enu_to_geodetic(x_east, y_north, z_up)

        now = datetime.utcnow()
        time_str = now.strftime("%H%M%S")

        lat_str, lat_hemi = self._decimal_to_nmea(lat, True)
        lon_str, lon_hemi = self._decimal_to_nmea(lon, False)

        gga_body = (
            f"GPGGA,{time_str},"
            f"{lat_str},{lat_hemi},"
            f"{lon_str},{lon_hemi},"
            f"{fix_quality},{num_sat},{hdop:.1f},"
            f"{alt:.1f},M,0.0,M,,"
        )

        checksum = 0
        for c in gga_body:
            checksum ^= ord(c)

        return f"${gga_body}*{checksum:02X}"
