import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import {Router} from '@angular/router';
import { SentimentService, Service } from '../_services/sentiment.service' 
import { RequestService } from '../_services/request.service'
import { environment } from '../../environments/environment';
import { DataService } from '../_services/data.service';
import { DataService2 } from '../_services/data2.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  public search_keyword: string = '';
  public showLoader = false;
  url = environment.BASE_URL + '/assets/app-assets/images/map.png';
  public body_background = "url(" + this.url +")";
  constructor(private dataService: DataService, private dataService2: DataService2, private service: Service, private router: Router, private requestService: RequestService) { 
    this.dataService.data.subscribe(data => {
      //do what ever needs doing when data changes
      if(data == true) {
        this.showLoader = true;
        this.body_background = "linear-gradient(rgba(72, 59, 59, 0.45),rgba(25, 25, 25, 0.45)), url(" + this.url +")";
      } else {
        this.showLoader = false;
        this.body_background = "url(" + this.url +")";
      }
      
    })
  }

  ngOnInit() {
    
  }

  search_query() {
    if (this.search_keyword != '') {
      this.showLoader = true;
      this.body_background = "linear-gradient(rgba(72, 59, 59, 0.45),rgba(25, 25, 25, 0.45)), url(" + this.url +")";
      this.requestService.getService('twitter/' + this.search_keyword)
        .subscribe(
          result => {
            this.dataService.updatedSearchedKeyword(this.search_keyword);
            this.service.setCountriesData(result['countries']);
            this.body_background = "url(" + this.url + ")";
            this.dataService2.updatedData(result['previous_result']);
            this.router.navigate(['analysis']);
          },
          error => {
            console.log(error);
          }
        );
    }
  }
}
