//
//  biomarkersApp.swift
//  biomarkers
//
//  Created by Rishit Vora on 29/11/23.
//

import SwiftUI
import HealthKit


@main
struct biomarkersApp: App {
	var body: some Scene {
		WindowGroup {
			ContentView()
				.onAppear {
					requestHealthKitAuth()
				}
		}
	}
	
	func getLastWeekStartDate(from date: Date = Date()) -> Date {
		return Calendar.current.date(byAdding: .day, value: -6, to: date)!
	}

	func createLastWeekPredicate(from endDate: Date = Date()) -> NSPredicate {
		let startDate = getLastWeekStartDate(from: endDate)
		print("startDate", startDate)
		print("endDate", endDate)
		return HKQuery.predicateForSamples(withStart: startDate, end: endDate)
	}
	
	func createAnchorDate() -> Date {
		// Set the arbitrary anchor date to Monday at 3:00 a.m.
		let calendar: Calendar = .current
		var anchorComponents = calendar.dateComponents([.day, .month, .year, .weekday], from: Date())
		let offset = (7 + (anchorComponents.weekday ?? 0) - 2) % 7
		
		anchorComponents.day! -= offset
		anchorComponents.hour = 3
		
		let anchorDate = calendar.date(from: anchorComponents)!
		print("anchorDate", anchorDate)
		
		return anchorDate
	}
	
	
	
	private func requestHealthKitAuth() {
		var healthStore: HKHealthStore?
		if HKHealthStore.isHealthDataAvailable() {
			healthStore = HKHealthStore()
		}
		let allTypes = Set([HKObjectType.workoutType(),
							HKQuantityType.quantityType(forIdentifier: .heartRate)!,
							HKQuantityType.quantityType(forIdentifier: .vo2Max)!,
							HKQuantityType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!,
							HKQuantityType.quantityType(forIdentifier: .restingHeartRate)!,
							HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)!,
							HKObjectType.quantityType(forIdentifier: .distanceWalkingRunning)!,
							HKObjectType.quantityType(forIdentifier: .stepCount)!])
		DispatchQueue.main.async {
			healthStore?.requestAuthorization(toShare: nil, read: allTypes) { (success, error) in
				if !success {
					let errorMessage = error
					print(errorMessage ?? "Undefined error")
				}
				else {
					print("hehe")
					let initialResultsHandler: (HKStatisticsCollection) -> Void = { (statisticsCollection) in
						var values: [Double] = []
						statisticsCollection.enumerateStatistics(from: getLastWeekStartDate(), to: Date()) { (statistics, stop) in
//							print("stats", statistics)
							let statisticsQuantity = statistics.averageQuantity()
//							print("stats qnt", statisticsQuantity)
//							var value = statisticsQuantity?.doubleValue(for: .count())	// steps
//							var value = statisticsQuantity?.doubleValue(for: HKUnit(from: "mL/min*kg"))	// vo2max
//							var value = statisticsQuantity?.doubleValue(for: HKUnit(from: "count/min"))	// hr, rhr
							var value = statisticsQuantity?.doubleValue(for: HKUnit(from: "ms"))	// hrv
							if (value == nil) {
								value = 0.0;
							}
							values.append(value!)
						}
						print("hi")
						print(values)
					}
					print("2")
					let query = HKStatisticsCollectionQuery(quantityType: HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!,
															quantitySamplePredicate: createLastWeekPredicate(),
															options: .discreteAverage,
															anchorDate: createAnchorDate(),
															intervalComponents: DateComponents(day: 1))
							
					// Set the results handler
					query.initialResultsHandler = { query, results, error in
						if let statsCollection = results {
							print("hahaha")
							print(statsCollection)
							initialResultsHandler(statsCollection)
						}
						else {
							print("oh no!")
							print(error!)
						}
					}
					print(query)
					 
					healthStore?.execute(query)
				}
			}
		}
		
	}
}

struct biomarkersAppView: View {
	var body: some View {
		Text("Hello World!")
	}
}

//print(HKHealthStore.isHealthDataAvailable())
