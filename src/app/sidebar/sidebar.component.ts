import { Component, OnInit } from '@angular/core';
import { RequestService } from '../_services/request.service';
import { Trends } from '../_models/trends';
import { Router } from '@angular/router';
import { Service } from '../_services/sentiment.service';
import { DataService } from '../_services/data.service';
import { DataService2 } from '../_services/data2.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  public trends: Array<Trends> = [];
  public searchValue: string =  '';
  public search_keyword = '';
  public previous_results = [];
  constructor(private dataService: DataService,private dataService2: DataService2, private service: Service, private router: Router, private requestService: RequestService) { 
    this.dataService.searchedKeyword.subscribe(data => {
      this.searchValue = data;
    })

    this.dataService2.data.subscribe(data => {
      console.log(data);
      this.previous_results = data;
    })
  }

  ngOnInit() {
    this.requestService.getService('trends')
        .subscribe(
        result => {
          let trends_result = result['trends'][0].trends;
          let i = 0;
          trends_result.forEach(element => {
            var english = /^(?=.*[a-zA-Z\d].*)[a-zA-Z\d!@#$%&*]{7,}$/;
            if(english.test(element.name) && i < 10) {
              let trend = new Trends();
              trend = element;
              this.trends.push(trend);
              i++;
            }
          });
        },
        error => {
          console.log(error);
        }
      );
  }

  loadPreviousResult(previous_result) {
    this.dataService.updatedData(false);
    this.service.setCountriesData(previous_result);
    this.router.navigate(['analysis']);
  }
  searchTrendsAnalysis(trend: string) {
    console.log('trend', trend);
      if(trend == '') {
        trend = this.search_keyword;
      }
      trend = trend.replace(/[^a-zA-Z 0-9]/g, "");
      this.dataService.updatedData(true);
      this.dataService.updatedSearchedKeyword(trend);
      this.requestService.getService('twitter/' + trend)
        .subscribe(
          result => {
            this.dataService.updatedData(false);
            this.service.setCountriesData(result['countries']);
            this.dataService2.updatedData(result['previous_result']);
            this.router.navigate(['analysis']);
          },
          error => {
            console.log(error);
          }
        );
  }
}
