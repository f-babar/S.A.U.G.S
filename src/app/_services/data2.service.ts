import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
@Injectable({
  providedIn: 'root'
})
export class DataService2 {
  private dataSource = new BehaviorSubject<Array<{}>>([]);
  data = this.dataSource.asObservable();

  constructor() { }

  updatedData(data: Array<{}>){
    this.dataSource.next(data);
  }
}
