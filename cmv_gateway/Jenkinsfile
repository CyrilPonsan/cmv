pipeline {
    agent any

    tools {
        nodejs 'nodejs20'
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: 'cmv_gateway', credentialsId: 'Git CMV Personal Access Token', url: 'https://github.com/CyrilPonsan/cmv.git'
            }
        }

        stage('Tests frontend') {
            steps {
                sh ''
                sh 'cd cmv/cmv_front'
                sh 'npm run test:unit'
            }
        }
}