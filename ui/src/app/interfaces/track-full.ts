import { Book } from "./book";
import { Track } from "./track";

export interface TrackFull extends Track {
    book: Book;
}
