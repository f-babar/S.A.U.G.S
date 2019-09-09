import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
@Injectable({
  providedIn: 'root'
})
export class DataService {
  private dataSource = new BehaviorSubject<boolean>(false);
  data = this.dataSource.asObservable();



  private searchedData = new BehaviorSubject<string>('');
  searchedKeyword = this.searchedData.asObservable();
  constructor() { }

  updatedData(data: boolean){
    this.dataSource.next(data);
  }
  
  updatedSearchedKeyword(data: string){
    this.searchedData.next(data);
  }

  
}
