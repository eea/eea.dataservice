
/*******************SQL for Data Dump*************************************/

Select
folder.relatedgid as '@relatedgid',
		--dataset start
		(select
		datasetgid as '@datasetgid',
		id as 'dataset_shortID',
		version as 'dataset_version',
		table_name as 'dataset_table_name',
		'<![CDATA['+ title +']]>' as 'dataset_title',
		'<![CDATA['+ note +']]>' as 'dataset_note',
		publish_date as 'dataset_publish_date',
		dataset.publish as 'dataset_publish_level',
		visible as 'dataset_visible',
			--metadata start
			(select 
			meta_type.typelabel as '@metadata_typelabel' ,
			meta_type.publish as 'metadata_type_publish_level',
			'<![CDATA['+ meta_details.text +']]>' as 'metadata_text',
			meta_details.publish as 'metadata_text_publish_level'
			from meta_details 
			inner join meta_type on meta_details.type=meta_type.typeid
			where dataset.datasetgid=meta_details.anygid and meta_details.type<>'110'
			for xml path('metadata_typelabel'),type),
			(select 
			meta_type.typelabel as '@metadata_typelabel' ,
			meta_type.publish as 'metadata_type_publish_level',
			'<![CDATA['+ PloneMigration_GeographicalCoverage.text +']]>' as 'metadata_text',
			PloneMigration_GeographicalCoverage.publish as 'metadata_text_publish_level'
			from PloneMigration_GeographicalCoverage
			inner join meta_type on PloneMigration_GeographicalCoverage.type=meta_type.typeid
			where dataset.datasetgid=PloneMigration_GeographicalCoverage.anygid
			for xml path('metadata_typelabel'),type),
			
			--metadata end
			--tableview start
			(
			select meta_tableview.tableviewGID as '@tableviewgid',
			'<![CDATA[' + meta_tableview.title + ']]>'  as 'tableview_title',
			meta_tableview.publish as 'tableview_publish_level',
				(select meta_tableview_sub.tableview_subgid as '@tableview_subgid',
				'<![CDATA[' + meta_tableview_sub.title + ']]>'  as 'tableviewsub_title',
				'<![CDATA[' + meta_tableview_sub.note + ']]>'   as 'tableviewsub_note',
				meta_tableview_sub.publish as 'tableviewsub_publish_level',
				meta_tableview_sub.totalrecords as 'tableviewsub_totalrecords'
				from meta_tableview_sub
				where meta_tableview_sub.id_main=meta_tableview.id
				for xml path('tableview_subgid'),type)
			from meta_tableview
			where dataset.id=meta_tableview.datasetid
			for xml path('tableviewgid'),type,root('tableGroup')),
			--tableview end
			--Download files start
			(
			select PloneMigration_DownloadFiles.sourcegid as '@tableview_subgid',
			PloneMigration_DownloadFiles.category as 'category',
			PloneMigration_DownloadFiles.id as 'download_file_shortID',
			PloneMigration_DownloadFiles.download_filesGID as 'download_file_downloadfilesgid',
			PloneMigration_DownloadFiles.filename as 'download_file_name',
			'http://dataservice.eea.europa.eu/download.asp?id=' + cast(PloneMigration_DownloadFiles.id as varchar(255)) as 'download_file_link',
			PloneMigration_DownloadFiles.filesize as 'download_file_size',
			PloneMigration_DownloadFiles.publish as 'download_file_publish_level',
			'<![CDATA[' + PloneMigration_DownloadFiles.title + ']]>' as 'download_file_title',
			'<![CDATA[' + PloneMigration_DownloadFiles.note + ']]>' as 'download_file_note',
			PloneMigration_DownloadFiles.agreementform as 'download_file_agreementform',
			PloneMigration_DownloadFiles.filesGID as 'download_file_filesgid'
			from PloneMigration_DownloadFiles
			where dataset.datasetgid=PloneMigration_DownloadFiles.datasetgid
			for xml path('tableview_subgid'),type,root('download_file')
			),
			--Download files end
			--TableViewMetadata start
			(
			select [PloneMigration_TableMetaData].tableview_subGID as '@tableview_subgid',
			[PloneMigration_TableMetaData].item as 'tableviewsub_metadata_item',
			'<![CDATA[' + [PloneMigration_TableMetaData].definition + ']]>' as 'tableviewsub_metadata_definition',
			'<![CDATA[' + [PloneMigration_TableMetaData].note + ']]>' as 'tableviewsub_metadata_note',
			[PloneMigration_TableMetaData].datatype as 'tableviewsub_metadata_datatype',
			[PloneMigration_TableMetaData].foreignkey as 'tableviewsub_metadata_primarykey'
			from [PloneMigration_TableMetaData]
			where dataset.datasetgid=[PloneMigration_TableMetaData].datasetgid
			for xml path('tableview_subgid'),type,root('Table_metadata')
			),
			--TableViewMetadata end
			--OtherServices start
			(
			select [PloneMigration_OtherServices].sourcetitle as '@other_services_category',
			'<![CDATA[' + [PloneMigration_OtherServices].title + ']]>' as 'other_services_title',
			'<![CDATA[' + [PloneMigration_OtherServices].note + ']]>' as 'other_services_note',
			'<![CDATA[' + [PloneMigration_OtherServices].url + ']]>' as 'other_services_url',
			[PloneMigration_OtherServices].publish as 'other_services_publish_level'
			from [PloneMigration_OtherServices]
			where dataset.datasetgid=[PloneMigration_OtherServices].datasetgid
			for xml path('other_services_category'),type,root('other_services')
			),
			--OtherServices end
			--Pivotview start
			(
			select [PloneMigration_PivotView].pivotviewGID as '@pivotview_GID',
			[PloneMigration_PivotView].id as 'pivotview_id',
			'<![CDATA[' + [PloneMigration_PivotView].title + ']]>' as 'pivotview_title',
			'<![CDATA[' + [PloneMigration_PivotView].note + ']]>' as 'pivotview_note',
			[PloneMigration_PivotView].publish as 'pivotview_publish_level',
			[PloneMigration_PivotView].Pivot_link as 'pivotview_link'
			from [PloneMigration_PivotView]
			where dataset.datasetgid=[PloneMigration_PivotView].datasetgid
			for xml path('pivotview_GID'),type,root('pivotview')
			),
			--Pivotview end
			--Link to M&G start
			(
			select [PloneMigration_linkDataSet_MapsGraphs].staticgisviewgid as '@staticgisview_GID',
			[PloneMigration_linkDataSet_MapsGraphs].id as 'staticgisview_id',
			'<![CDATA[' + [PloneMigration_linkDataSet_MapsGraphs].title + ']]>' as 'staticgisview_title',
			'<![CDATA[' + [PloneMigration_linkDataSet_MapsGraphs].note + ']]>' as 'staticgisview_note',
			[PloneMigration_linkDataSet_MapsGraphs].publish as 'staticgisview_publish_level',
			[PloneMigration_linkDataSet_MapsGraphs].staticgisview_link as 'staticgisview_link'
			from [PloneMigration_linkDataSet_MapsGraphs]
			where dataset.datasetgid=[PloneMigration_linkDataSet_MapsGraphs].datasetgid
			for xml path('staticgisview_GID'),type,root('staticgisview')
			),
			--Link to M&G end
			--QualityStamp start
			(select qualityname as 'quality_name',
			description as 'quality_description',
			qualityvalue as 'quality_value'
			from [PloneMigration_QualityStamp]
			where dataset.datasetgid=[PloneMigration_QualityStamp].gid
			for xml path(''),type,root('quality_stamp')
			)
			--QualityStamp end

		from meta_dataset as dataset
		where folder.relatedgid=dataset.relatedgid 
		for xml path('datasetgid'),type)
		--dataset end
from meta_dataset as folder 
group by folder.relatedgid
for xml Path('relatedgid'),type,root('data')