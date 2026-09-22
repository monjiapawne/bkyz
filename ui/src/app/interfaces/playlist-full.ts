import { Playlist } from "./playlist";
import { TrackFull } from "./track-full";

export interface PlaylistFull extends Playlist {
    tracks: TrackFull[];
}
