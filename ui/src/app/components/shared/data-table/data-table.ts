import { Component, input, output } from '@angular/core';

export interface Column {
  key: string;
  label: string;
}

@Component({
  selector: 'app-data-table',
  templateUrl: './data-table.html',
})
export class DataTable {

  columns = input.required<Column[]>();
  rows = input.required<any[]>();
  editable = input(false);
  edit = output<any>();

  display(value: unknown) {
    return Array.isArray(value) ? value.join(', ') : value;
  }
}
